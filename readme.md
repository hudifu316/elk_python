# BCNEWS

Scapyでニュースクローリングして、Elasticsearchに投入するデモ
投入した記事は以下のreactアプリから見ることができる
https://github.com/hudifu316/react_elk

### 前提条件
以下の環境で動作確認してます
- docker/docker-composeが入っている
- anacondaでjupyterが入っている
- conda/pipで以下パッケージが入ってる
    python3
    scrapy
    ginza
    json
    ndjson

```
./
├─bcnews        scrapy（ニュースクローラ）のコードセット
│  └─spiders
├─elsdata       elasticsearchのindexデータの永続先
├─lstconf       logstash用の設定ファイル(logstash.conf)の配置先
└─lstinput      logstashでelasticsearchに投入するデータの格納先
```
### 起動
- dockerイメージでelkスタックを起動する
    `docker-compose -f ./docker-compose.yml up -d`
    - elasticsearchの正常起動確認
        ブラウザもしくはcurlで[localhost:9200](http://localhost:9200)を確認する
    - kibanaの正常起動確認
        ブラウザで[localhost:5601](http://localhost:5601)で確認する
- elasticsearchにindex templateを投入しておく。（日本語のanalyzerをkuromojiに変更するため）
    ```
    curl -H "Content-Type: application/json" -XPUT 'localhost:9200/_template/bcnews_tmpl' -d \
    '{
        "index_patterns": "bcnews*",
        "mappings": {
            "properties": {
                "title": {
                    "analyzer": "kuromoji",
                    "type": "text"
                },
                "body": {
                    "analyzer": "kuromoji",
                    "type": "text"
                }
            }
        },
        "aliases": {
            "bcnews": {}
        }
    }'
    ```
- Scrapyでニュースを取得
    `scrapy crawl neweconomy -o bcnews20210524.jl`
    結果サンプルをいくつか置いてます。
- logstashに食わせられる形式に変換(bcnews*.jl)
    - このデモではJupyterを使用（news.ipynb）
    結果サンプルをいくつか置いてます。(bcnews*.json)
    - ginza(spacyモデル)で記事本文のキーワード抽出を実施してtagsフィールドへ格納
    - 拡張子をjl→jsonへ変換してlogstashの監視ディレクトリ(lstinput)に出力
- logstashでelasticsearchへ投入
    - logstashのコンテナが./lstinputを監視しており、*.jsonファイルが書き込まれると自動的にelasticsearchへindex
    サンプルでは、置いているbcnews*.jsonファイルをlistinputフォルダへ入れると動きます。
- kibanaのダッシュボードで見る方法
    kibana側でもelasticsearch indexに対応したindexパターンを作成する必要がある。
    - ブラウザで[kibana](http://localhost:5601/app/management/kibana/indexPatterns)にアクセス
    - create index patternボタン押下
        - index pattern name: bcnews-*
        - time field: date
        - create index pattern ボタンでindex patternを作成
