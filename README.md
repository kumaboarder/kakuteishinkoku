# 確定申告お助け用
エンさんツールからCSV出力をマージしてある程度クリプタクト用に加工・成形する
https://twitter.com/engr5050/status/1575748809719570432

* CSVファイルのマージ
* 不要なカラムの削除
* クリプタクト用のカラムに変換


## chatGTP用

* 作成されたCSVを別のCSVへ変換する関数を作成しましょう。
  * ルールは以下です。
    * Value(Total JPY) or Value(JPY)をPriceへ
    * TimeはTimestampへ
    * Event TypeはActionへ

