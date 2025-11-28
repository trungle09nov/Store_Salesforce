import requests
import json

# --- Cấu hình ---
INSTANCE_URL = ""
ACCESS_TOKEN = ""

# SOQL query
SOQL_QUERY = "SELECT Id, Name, FirstName, LastName, IsPersonAccount FROM Account"

# file output
OUTPUT_FILE = "./data/accounts_data.json"

# --- Header ---
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# --- URL batch đầu ---
url = f"{INSTANCE_URL}/services/data/v65.0/query/?q={SOQL_QUERY}"

all_records = []

while url:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        break

    data = response.json()

    # Thêm record vào list
    all_records.extend(data.get("records", []))

    # Kiểm tra batch tiếp theo
    next_url = data.get("nextRecordsUrl")
    if next_url:
        url = f"{INSTANCE_URL}{next_url}"
    else:
        url = None

# --- Lưu JSON ---
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_records, f, ensure_ascii=False, indent=2)

print(f"Tổng record lấy được: {len(all_records)}")
print(f"Lưu xong vào file: {OUTPUT_FILE}")
