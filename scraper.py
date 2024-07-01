# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
import csv

# 取得したいデータ
# items = ["メーカー", "モデル", "販売価格", "クラブ種別", "番手", "シャフト", "フレックス", "年式", "ヘッドロフト角(°)", "クラブ重量(g)", "ヘッドライ角(°)", "利き手", "ヘッド体積(cc)", "シャフト長(インチ)", "性別"]
base_url = 'https://www.golfpartner.jp'
def get_product_urls(first_url):
    product_urls = []
    url = first_url
    while url:
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.content, 'html.parser')

        # 商品リンクを取得
        product_links = soup.select('a.goods_name_')  # 'goods_name_' クラスを持つ <a> タグを選択
        for link in product_links:
            product_urls.append(base_url + link['href'])

        # 次のページへのリンクを取得
        next_page = soup.find('a', rel='next')
        url = next_page['href'] if next_page else None
        if url:
            url = base_url + url # 相対パスを絶対パスに変換
    return product_urls


first_url = 'https://www.golfpartner.jp/shop/usedgoods/?store_code=9153' # 9153の店舗在庫を一気に表示

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

def fetch_golf_club_data(url):
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.content, 'html.parser')
    # メーカー、モデル、販売価格を取得
    club = {
        '商品コード': soup.select_one('.plu_code_').get_text(strip=True).split('：')[1] if soup.select_one('.plu_code_') else 'N/A',
        'メーカー': soup.select_one('.goods_name2_').get_text(strip=True) if soup.select_one('.goods_name2_') else 'N/A',
        'モデル': soup.select_one('.goods_name_').get_text(strip=True) if soup.select_one('.goods_name_') else 'N/A',
        '販売価格': soup.select_one('.goods_detail_price_').get_text(strip=True) if soup.select_one('.goods_detail_price_') else 'N/A',
    }
    # スペック、メーカーカタログ情報、取り扱い店舗情報を取得
    club = club | fetch_from_table(soup, 'desc_tbl_')
    return club

def save_to_csv(clubs, filename):
    if not clubs:
        return
    
    headers = clubs[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in clubs:
            writer.writerow(row)

cwd = os.getcwd()

if __name__=="__main__":
    
    clubs = []
    i = 1
    urls = get_product_urls(first_url)
    for url in urls:
        print(f"{i}/{len(urls)}本目を読み取り中")
        clubs.append(fetch_golf_club_data(url))
        i += 1
    save_to_csv(clubs, os.path.join(cwd, "club_database.csv"))

print("----done!!")