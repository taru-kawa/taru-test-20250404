import requests
import urllib.parse
import os
from datetime import datetime
import csv
import time  # time.sleep() を使用する場合

# 設定
baseurl = "orca.cybereason.net"  # 実際の URL に置き換えてください
port = "443"
username = "cybereason-api-user@orca-inc.co.jp"  # 実際のユーザー名に置き換えてください
password = "v2Tb%FtgtG$&gd+6"  # 実際のパスワードに置き換えてください

# requests セッションの開始
session = requests.Session()

# Cybereason API ログイン
login_url = f"https://{baseurl}:{port}/login.html"
body = {
    "username": username,
    "password": password
}

try:
    # Accept ヘッダーは 'application/x-www-form-urlencoded' にしておくのが安全
    response = session.post(login_url, data=urllib.parse.urlencode(body), headers={'Content-Type': 'application/x-www-form-urlencoded'}, verify=False)
    response.raise_for_status()
    print("✅ Login successful.")
except requests.exceptions.RequestException as e:
    print(f"❌ Login failed: {e}")
    exit()

# フィルターなしでCSV取得 (GETリクエスト)
try:
    query_url = f"https://{baseurl}:{port}/rest/sensors/download/csv"
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M')
    csv_filename = f"CybereasonSensors_{timestamp}.csv"
    csv_filepath = os.path.join(os.getcwd(), csv_filename)

    # Accept ヘッダーを修正
    headers = {
        'Accept': '*/*'  # すべてのコンテンツタイプを受け入れる
        # 'Accept': 'text/csv',  # 明示的に指定する場合。指定しなくても動くサーバも多い
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',  # ブラウザの User-Agent を設定
        # 'Referer': f'https://{baseurl}:{port}/' # 必要な場合
        # ... 他のヘッダー ...
    }

    query_response = session.get(query_url, headers=headers, verify=False, timeout=None)
    query_response.raise_for_status()
    with open(csv_filepath, 'w', encoding='utf-8') as f:
        f.write(query_response.text)
    print(f"✅ CSV downloaded to: {csv_filepath}")

    # CSVファイルの読み込みと処理
    online_machines = set()
    offline_machines = set()
    with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        # 列名を小文字に変換
        if reader.fieldnames:  # fieldnames が None でないことを確認
            reader.fieldnames = [fieldname.lower() for fieldname in reader.fieldnames]
        for row in reader:
            machine_name = row.get("machine name")  # 小文字で指定
            sensor_status = row.get("sensor status")  # 小文字で指定
            if machine_name and sensor_status:
                # 前後の空白を削除し、小文字に変換して比較
                if sensor_status.strip().lower() == "online":
                    online_machines.add(machine_name)
                elif sensor_status.strip().lower() == "offline":
                    offline_machines.add(machine_name)

    # 結果を出力
    print("\nOnline Machines:")
    for machine in online_machines:
        print(f"- {machine}")
    print(f"\nTotal Online Machines: {len(online_machines)}")

    print("\nOffline Machines:")
    for machine in offline_machines:
        print(f"- {machine}")
    print(f"\nTotal Offline Machines: {len(offline_machines)}")

except requests.exceptions.RequestException as e:
    print(f"❌ CSV ダウンロードまたは Machine name 抽出に失敗しました: {e}")
except IOError as e:
    print(f"❌ ファイル入出力エラーが発生しました: {e}")
except csv.Error as e:
    print(f"❌ CSV 処理エラーが発生しました: {e}")
finally:
    # CSVファイルを削除 (削除)
    # if os.path.exists(csv_filepath):
    #     os.remove(csv_filepath)
    #     print(f"🗑️ {csv_filepath} を削除しました。")
    pass  # 何もしないように pass を追加