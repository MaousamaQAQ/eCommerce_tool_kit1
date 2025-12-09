import requests
import time
import os
import csv
import json
import traceback
from datetime import datetime
import pandas as pd

# 让 DataFrame 输出显示所有列
pd.set_option("display.max_columns", None)

# 让 DataFrame 输出显示前 50 行
pd.set_option("display.max_rows", 50)

now = datetime.now()

time_str = now.strftime("%Y_%m_%d_%H_%M_%S")
date_str = now.strftime("%Y-%m-%d")


# -----------------------------
# 读取 param.txt
# -----------------------------
param_file = "param.txt"

if not os.path.exists(param_file):
    raise FileNotFoundError(f"{param_file} 不存在！请确保在同级目录下。")

with open(param_file, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()
    if len(lines) < 2:
        raise ValueError("param.txt 中至少需要两行：第一行 API key，第二行网页 URL")
    API_KEY = lines[0].strip()
    BASE_URL = lines[1].strip().rstrip("/")

HEADERS = {"apikey": API_KEY}

# -----------------------------
# 获取国家
# -----------------------------
def get_countries():
    url = f"{BASE_URL}/countries/get"
    res = requests.get(url, headers=HEADERS)
    data = res.json()
    return data.get("countries", []) if not data.get("error") else []

# -----------------------------
# 获取产品组
# -----------------------------
def get_product_groups():
    url = f"{BASE_URL}/product_groups/get"
    res = requests.get(url, headers=HEADERS)
    data = res.json()
    return data.get("product_groups", []) if not data.get("error") else []

# -----------------------------
# 获取产品数据
# -----------------------------
def get_products_by_country_group(country_code, product_group, date=f"{date_str}"):
    url = f"{BASE_URL}/prices/{country_code}/{product_group}/get?date={date}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print(f"请求失败: {country_code} - {product_group}")
        return []
    data = res.json()
    return data.get("data", [])

# -----------------------------
# 批量抓取
# -----------------------------
def fetch_all_data():
    all_data = []
    countries = get_countries()
    product_groups = get_product_groups()

    for country in countries:
        country_code = country['country_code']
        country_name = country['country']
        print(f"处理国家: {country_name}")

        for group in product_groups:
            group_name = group['group']
            print(f"  产品组: {group_name}")
            products = get_products_by_country_group(country_code, group_name)
            for p in products:
                p['country'] = country_name
                p['product_group'] = group_name
                all_data.append(p)
            time.sleep(0.5)

    return all_data

# -----------------------------
# 保存 CSV
# -----------------------------
def save_to_csv(data, filename="all_products_data.csv"):
    # 提取 CSV 字段
    fieldnames = [
        "country", "product_group", "name", "title", "model", "storage", "ram",
        "color", "screen_size_decimal", "network", "partner", "url",
        "regular_price", "promotion_price", "availability"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in data:
            # 每个产品可能有多个 info
            infos = item.get("info", [])
            if not infos:
                row = {key: item.get(key, "") for key in fieldnames}
                writer.writerow(row)
            else:
                for info in infos:
                    row = {
                        "country": item.get("country", ""),
                        "product_group": item.get("product_group", ""),
                        "name": item.get("name", ""),
                        "title": item.get("title", ""),
                        "model": item.get("model", ""),
                        "storage": item.get("storage", ""),
                        "ram": item.get("ram", ""),
                        "color": item.get("color", ""),
                        "screen_size_decimal": item.get("screen_size_decimal", ""),
                        "network": item.get("network", ""),
                        "partner": info.get("partner", ""),
                        "url": info.get("url", ""),
                        "regular_price": info.get("regular_price", ""),
                        "promotion_price": info.get("promotion_price", ""),
                        "availability": info.get("availability", "")
                    }
                    writer.writerow(row)

    print(f"数据已保存到 {filename}")

# -----------------------------
# 主程序
# -----------------------------
if __name__ == "__main__":
    for i in range(5):
        try:
            all_products_data = fetch_all_data()
            break
        except Exception as e:
            print("抓取数据时发生错误：", e)
            traceback.print_exc()  # 打印完整错误堆栈

    # 先打印 JSON
    print(json.dumps(all_products_data, ensure_ascii=False, indent=2))

    # 转为 DataFrame
    df = pd.DataFrame(all_products_data)

    print(df)
    print("当前 df 行数：", len(df))
    # 展开 info 字段（如果有），保持与原逻辑一致
    if "info" in df.columns:
        df = df.explode("info", ignore_index=True)
        info_df = pd.json_normalize(df["info"])
        df = pd.concat([df.drop(columns=["info"]), info_df], axis=1)
    print("当前 df 行数：", len(df))
    # 去重（按 model + partner）
    df = df.drop_duplicates(subset=["model", "partner"], keep="first")
    print("当前 df 行数：", len(df))

    # 转回字典列表，继续给 save_to_csv 使用
    all_products_data = df.to_dict(orient="records")
    # ---- 插入代码结束 ----

    # 确保 download 文件夹存在
    download_dir = "download"
    os.makedirs(download_dir, exist_ok=True)
    # 拼接路径
    output_path = os.path.join(download_dir, f"output_{time_str}.csv")
    # 保存为 CSV
    save_to_csv(all_products_data, filename=output_path)

