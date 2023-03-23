import os
import math
import numpy as np
import pandas as pd
from typing import List
import configparser

def merge_csv_files(folder_path: str) -> pd.DataFrame:
    # フォルダ内のすべてのCSVファイルを読み込む
    csv_files: List[str] = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # CSVファイルをマージする
    df_list: List[pd.DataFrame] = []
    for file in csv_files:
        file_path: str = os.path.join(folder_path, file)
        df: pd.DataFrame = pd.read_csv(file_path)
        df_list.append(df)

    merged_df: pd.DataFrame = pd.concat(df_list, ignore_index=True).sort_values(by=["Time","Contract Address"])
    
    return merged_df

def convert_csv(csvData: pd.DataFrame) -> pd.DataFrame:
    # クリプタクト用の列を追加(Timestamp)
    csvData['Timestamp'] = csvData['Time']

    # クリプタクト用の列を追加(Timestamp)
    # Mintが含まれていたらBUY
    csvData['Action'] = csvData['Event Type'].str \
        .replace('.*Mint.*', 'BUY', regex=True) \
        .replace('.*Sell.*', 'SELL', regex=True) \
        .replace('.*Claim.*', 'BUY', regex=True) \
        .replace('.*BidWon.*', 'BUY', regex=True) \
        .replace('.*Run.*', 'BUY', regex=True)
    # クリプタクト用の列を追加(Source)
    csvData['Source'] = csvData['Title']

    # クリプタクト用の列を追加(Base)
    # Titleの#以前の先頭10文字
    csvData['Base'] = 'USER-' + csvData['Title'].str.split('#').str[0].str[:10]

    # クリプタクト用の列を追加(Volume)
    # transform_volume_valueに従って変換
    csvData['Volume'] = csvData.apply(transform_volume_value, axis=1)

    # クリプタクト用の列を追加（Price）
    # 判断用なので数値変換して変換できなければ空
    # 計算用なので数値変換して変換できなければ0を入れる
    # csvData['Value(JPY)'] = pd.to_numeric(csvData['Value(JPY)'], errors='coerce')
    # csvData['Value(Total JPY)'] = pd.to_numeric(csvData['Value(Total JPY)'], errors='coerce')
    # PriceにはValue(Total JPY)、Value(JPY)の合計値
    # csvData['Price'] = csvData.apply(lambda row: row['Value(Total JPY)'] + row['Value(JPY)'] if pd.notnull(row['Value(Total JPY)']) else row['Value(JPY)'], axis=1)
    csvData['Price'] = csvData.apply(transform_price_value, axis=1)


    # クリプタクト用の列を追加（Counter）
    # csvData['Counter'] = csvData.apply(transform_counter_value, axis=1)
    csvData = csvData.assign(Counter="JPY")

    # クリプタクト用の列を追加（Fee）
    csvData['Fee'] = csvData['TX Fee(JPY)']

    # クリプタクト用の列を追加(FeeCcy)
    csvData = csvData.assign(FeeCcy="JPY")

    # クリプタクト用の列を追加(Comment)
    csvData['Comment'] = csvData['Transaction Hash']

    return csvData

# 変換ロジックを定義する関数の作成(Volume)
def transform_volume_value(row):
    if not row['Bulk'] == '-':
        return row['Bulk']
    elif row['Action'] == 'BUY' or row['Action'] == 'SELL':
        return 1
    else:
        return 0
# 変換ロジックを定義する関数の作成(Price)
def transform_price_value(row):
    # ETHの場合
    if not pd.isnull(row['1ETH Price(USD)']):
        ret = row['Value(JPY)']
    # polygonの場合
    else:
        ret = row['Value(Total JPY)']
    return ret
# 変換ロジックを定義する関数の作成(Counter)
def transform_counter_value(row):
    # ETHの場合
    if not row['1ETH Price(USD)'] == math.nan:
        return 'ETH'
    # polygonの場合
    else:
        return 'JPY'

if __name__ == '__main__':
    # 設定ファイルからCSVファイルがあるフォルダのパスを読み込む
    config: configparser.ConfigParser = configparser.ConfigParser()
    config.read('../env/config.ini')
    folder_path: str = config.get('DEFAULT', 'CSV_FOLDER_PATH')

    # CSVファイルをマージする
    merged_df: pd.DataFrame = merge_csv_files(folder_path)
    # merged_df.to_csv(f"{folder_path}/merged.csv", index=False)
    print(merged_df.head())
    # CSVデータを変換する
    converted_df:pd.DataFrame = convert_csv(merged_df)
    converted_df.to_csv(f"{folder_path}/output/converted.csv", index=False)
    print(converted_df.head())
    print(converted_df['Action'].head())    