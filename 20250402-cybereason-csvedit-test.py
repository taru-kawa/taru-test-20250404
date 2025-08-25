import requests
import urllib.parse
import os
from datetime import datetime
import csv

# 設定
baseurl = "orca.cybereason.net"
port = "443"
username = "cybereason-api-user@orca-inc.co.jp"
password = "v2Tb%FtgtG$&gd+6"

# Cybereason API ログイン
login_url = f"https://{baseurl}:{port}/login.html"
body = {
    "username": username,
    "password": password
}

try:
    response = requests.post(login_url, data=urllib.parse.urlencode(body), headers={'Content-Type': 'application/x-www-form-urlencoded'})
    response.raise_for_status()  # HTTPエラーをチェック
    my_websession = response.cookies
    print("✅ Login successful.")
except requests.exceptions.RequestException as e:
    print(f"❌ Login failed: {e}")
    exit()

# フィルターなしでCSV取得 (GETリクエスト)
query_url = f"https://{baseurl}:{port}/rest/sensors/download/csv"
timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M')
csv_filename = f"CybereasonSensors_{timestamp}.csv"
csv_filepath = os.path.join(os.getcwd(), csv_filename)

try:
    query_response = requests.get(query_url, headers={'Content-Type': 'text/csv'}, cookies=my_websession, timeout=None)
    query_response.raise_for_status()
    with open(csv_filepath, 'w', encoding='utf-8') as f:
        f.write(query_response.text)
    print(f"✅ CSV downloaded to: {csv_filepath}")

    # CSVファイルの読み込みと処理
    machine_name_counts = {}
    with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            machine_name = row.get("Machine name")
            if machine_name:
                machine_name_counts[machine_name] = machine_name_counts.get(machine_name, 0) + 1

    # 重複する Machine name を抽出
    duplicate_machine_names = {name: count for name, count in machine_name_counts.items() if count > 1}

    # 結果を出力
    if duplicate_machine_names:
        print("以下の Machine name が複数存在します:")
        for name, count in duplicate_machine_names.items():
            print(f"{name} (Count: {count})")
    else:
        print("重複する Machine name はありません。")

except requests.exceptions.RequestException as e:
    print(f"❌ CSV ダウンロードまたは Machine name 抽出に失敗しました: {e}")
except IOError as e:
    print(f"❌ ファイル入出力エラーが発生しました: {e}")
except csv.Error as e:
    print(f"❌ CSV 処理エラーが発生しました: {e}")
finally:
    # CSVファイルを削除
    if os.path.exists(csv_filepath):
        os.remove(csv_filepath)
        print(f"🗑️ {csv_filepath} を削除しました。")