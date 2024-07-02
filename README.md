# golpa_database
店番9153の在庫クラブをcsvファイルに保存 --- scraper.py

## How To Use
1. scraper.pyをscraper.pyxに変換
2. setup.pyを作成
3. コンパイル
    $ python setup.py build_ext --inplace
4. 使用
    $ python3
    $ from scraper import fetch_and_write
    $ fetch_and_write()