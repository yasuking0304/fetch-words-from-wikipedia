# Fetch title word from Wikipedia

## Usages
This is the test code to learn the title from the database dump of the Japanese Wikipedia.

It can be used as a source material for creating a user dictionary of MOZC.

## How to use
1. Install Python 3

2. Install requests from pip
    ```
    pip3 install requests
    ```
3. Install requests from flask
    ```
    pip3 install flask
    ```
4. Uncomment and run the items you want to extract from the source

## Remarks
If the dump file(jawiki-latest-pages-articles.xml.bz2) of the Japanese Wikipedia [database dump location](https://dumps.wikimedia.org/jawiki/latest/) has been downloaded to your local PC, search from your local PC, If it has not been downloaded, search for the file directly from the Wikipedia location.  
　If you use a local PC download file, use port 8080. Depending on the execution environment, change the port.

## License

**MIT**

---
## 使い道
日本語版Wikipediaのデータベース・ダンプから、タイトルを習得するテストコードです。

mozcのユーザ辞書作成のための元ネタなどに使えます。

## 使い方
1. Python3をインストールする

2. requestsを pipインストールする
    ```
    pip3 install requests
    ```
3. flaskを pipインストールする
    ```
    pip3 install flask
    ```
4. ソースから抽出したい項目のコメントを外して実行する

## 備考
日本語版Wikipediaの[データベース・ダンプ場所](https://dumps.wikimedia.org/jawiki/latest/)の（jawiki-latest-pages-articles.xml.bz2）がローカルPCにダウンロードされている場合、ローカルPCからサーチ、ダウンロードされていない場合はwikipediaの置き場から直接ファイルサーチします。  
　ローカルPCのダウンロードファイルを使用する場合、8080ポートを使用します。実行環境によってはポート変更してください。


## License

**MIT**
