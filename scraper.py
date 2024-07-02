# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
import csv
from tqdm import tqdm

# 取得したいデータ
# items = ["メーカー", "ヘッドモデル", "販売価格", "クラブ種別", "番手", "シャフト", "フレックス", "年式", "ヘッドロフト角(°)", "クラブ重量(g)", "ヘッドライ角(°)", "利き手", "ヘッド体積(cc)", "シャフト長(インチ)", "性別"]
base_url = 'https://www.golfpartner.jp'

# クラブ情報ページのリンクを取得
def get_product_urls(first_url):
    product_urls = []
    url = first_url
    
    bar = tqdm(range(550000)) # 中古クラブ在庫数55万本
    bar.set_description('Now Loading Product Links')
    while url:
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.content, 'html.parser')

        # 商品リンクを取得
        product_links = soup.select('a.goods_name_')  # 'goods_name_' クラスを持つ <a> タグを選択
        
        
        for link in product_links:
            product_urls.append(base_url + link['href'])
            bar.update(1)

        # 次のページへのリンクを取得
        next_page = soup.find('a', rel='next')
        url = next_page['href'] if next_page else None
        if url:
            url = base_url + url # 相対パスを絶対パスに変換        
    bar.close()
    return product_urls


first_url = 'https://www.golfpartner.jp/shop/usedgoods/?store_code=9153' # 9153の店舗在庫を一気に表示

# table要素からクラブ情報取得
def fetch_from_table(soup, class_='desc_tbl_'):
    # スペック、メーカーカタログ情報、取り扱い店舗情報を取得
    tables = soup.find_all('table', class_=class_) 
    club = {}
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            headers = row.find_all('th')
            data = {
                headers[i].get_text(strip=True): cells[i].get_text(strip=True) if i < len(cells) else 'N/A' for i in range(len(headers))
            }
            club = club | data
    return club
# クラブ情報を取得
def fetch_golf_club_data(url):
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.content, 'html.parser')
    # シャフト名取得用
    first_table = soup.find('table', class_='desc_tbl_')
    span = first_table.find('span') # 1つ目のtableの唯一のspanにシャフト名が格納されている。
    # メーカー、モデル、販売価格、シャフトを取得
    club = {
        '商品コード': soup.select_one('.plu_code_').get_text(strip=True).split('：')[1] if soup.select_one('.plu_code_') else 'N/A',
        'メーカー': soup.select_one('.goods_name2_').get_text(strip=True) if soup.select_one('.goods_name2_') else 'N/A',
        'ヘッドモデル': soup.select_one('.goods_name_').get_text(strip=True) if soup.select_one('.goods_name_') else 'N/A',
        '販売価格': soup.select_one('.goods_detail_price_').get_text(strip=True).split('：')[1].replace(',', '').replace('円', '') if soup.select_one('.goods_detail_price_') else 'N/A',
        'シャフトモデル': span.get_text(strip=True) if span else 'N/A',
    }
    # スペック、メーカーカタログ情報、取り扱い店舗情報を取得
    club = club | fetch_from_table(soup, 'desc_tbl_')
    
    # ヘッド上部の情報が傷状態に格納されているので
    club['ヘッド上部'] = club['傷状態']
    club.pop('傷状態')
    
    return club

# 取得した情報をcsvファイルへ変換して保存
def save_to_csv(clubs, filename):
    if not clubs:
        return
    
    headers = clubs[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in clubs:
            writer.writerow(row)


# まとめ
def fetch_and_write():

    clubs = []
    i = 1
    urls = get_product_urls(first_url)
    
    bar = tqdm(total=len(urls))
    bar.set_description('Now Loading Product Info')
    
    for url in urls:
        # print(f"{i}/{len(urls)}本目を読み取り中")
        clubs.append(fetch_golf_club_data(url))
        i += 1
        bar.update(1)
    save_to_csv(clubs, os.path.join(os.getcwd(), "club_database.csv"))
    bar.close()

if __name__=="__main__":
    fetch_and_write()
    print("----\ndone!!\n----")