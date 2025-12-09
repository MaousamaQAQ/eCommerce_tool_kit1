import requests
import time
import os
import csv
import json
import traceback
from datetime import datetime, timedelta
import pandas as pd

# 让 DataFrame 输出显示所有列
pd.set_option("display.max_columns", None)

# 让 DataFrame 输出显示前 50 行
pd.set_option("display.max_rows", 50)

now = datetime.now()
time_str = now.strftime("%Y_%m_%d_%H_%M_%S")

# -----------------------------
# 自动重试 GET 请求
# -----------------------------
def safe_get(url, headers=None, max_retries=5, timeout=15):
    for attempt in range(1, max_retries + 1):
        try:
            res = requests.get(url, headers=headers, timeout=timeout)
            res.raise_for_status()
            return res
        except Exception as e:
            print(f"请求失败（第 {attempt} 次）：{e}")
            if attempt < max_retries:
                time.sleep(2)
            else:
                print("已达最大重试次数，跳过此请求。")
                return None


# -----------------------------
# 读取 param.txt
# -----------------------------
param_file = "param.txt"

if not os.path.exists(param_file):
    raise FileNotFoundError(f"{param_file} 不存在！请确保在同级目录下。")

with open(param_file, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()
    if len(lines) < 4:
        raise ValueError("param.txt 必须至少包含四行：API key、URL、开始日期、结束日期")

    API_KEY = lines[0].strip()
    BASE_URL = lines[1].strip().rstrip("/")
    START_DATE_STR = lines[2].strip()
    END_DATE_STR = lines[3].strip()

HEADERS = {"apikey": API_KEY}

# -----------------------------
# 解析日期（格式 YYYY/MM/DD）
# -----------------------------
try:
    start_date = datetime.strptime(START_DATE_STR, "%Y/%m/%d")
    end_date = datetime.strptime(END_DATE_STR, "%Y/%m/%d")
except Exception:
    raise ValueError("param.txt 第 3、4 行日期格式错误，必须为 YYYY/MM/DD")


# -----------------------------
# 获取国家
# -----------------------------
def get_countries():
    url = f"{BASE_URL}/countries/get"
    res = safe_get(url, headers=HEADERS)
    if res is None:
        return []
    data = res.json()
    return data.get("countries", []) if not data.get("error") else []


# -----------------------------
# 获取产品组
# -----------------------------
def get_product_groups():
    url = f"{BASE_URL}/product_groups/get"
    res = safe_get(url, headers=HEADERS)
    if res is None:
        return []
    data = res.json()
    return data.get("product_groups", []) if not data.get("error") else []


# -----------------------------
# 获取产品数据（按国家 + 产品组 + 日期）
# -----------------------------
def get_products_by_country_group(country_code, product_group, date_str):
    url = f"{BASE_URL}/prices/{country_code}/{product_group}/get?date={date_str}"
    res = safe_get(url, headers=HEADERS)
    if res is None:
        print(f"请求失败: {country_code} - {product_group} on {date_str}")
        return []
    data = res.json()
    return data.get("data", [])


# -----------------------------
# 批量抓取（加日期）
# -----------------------------
def fetch_all_data(date_str):
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
            products = get_products_by_country_group(country_code, group_name, date_str)

            for p in products:
                p['country'] = country_name
                p['product_group'] = group_name
                p['date'] = date_str
                all_data.append(p)

            time.sleep(0.5)

    return all_data


# -----------------------------
# 保存 CSV
# -----------------------------
def save_to_csv(data, filename="all_products_data.csv"):
    fieldnames = [
        "date", "country", "product_group", "name", "title", "model",
        "storage", "ram", "color", "screen_size_decimal", "network",
        "partner", "url", "regular_price", "promotion_price",
        "availability"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in data:
            infos = item.get("info", [])
            if not infos:
                row = {key: item.get(key, "") for key in fieldnames}
                writer.writerow(row)
            else:
                for info in infos:
                    row = {
                        "date": item.get("date", ""),
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
# 主程序（循环日期）
# -----------------------------
if __name__ == "__main__":

    all_products_data = []

    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        print(f"\n==== 正在抓取日期：{date_str} ====")

        try:
            day_data = fetch_all_data(date_str)
            all_products_data.extend(day_data)
        except Exception as e:
            print("抓取数据时发生错误：", e)
            traceback.print_exc()

        current += timedelta(days=1)

    # -----------------------------
    # pandas 处理
    # -----------------------------
    df = pd.DataFrame(all_products_data)
    print(df)
    print("当前 df 行数：", len(df))

    if "info" in df.columns:
        df = df.explode("info", ignore_index=True)
        info_df = pd.json_normalize(df["info"])
        df = pd.concat([df.drop(columns=["info"]), info_df], axis=1)
    print("展开 info 后行数：", len(df))

    df = df.drop_duplicates(subset=["model", "partner", "date"], keep="first")
    print("去重后行数：", len(df))

    all_products_data = df.to_dict(orient="records")

    # -----------------------------
    # 保存文件
    # -----------------------------
    download_dir = "download"
    os.makedirs(download_dir, exist_ok=True)

    output_path = os.path.join(download_dir, f"output_{time_str}.csv")
    save_to_csv(all_products_data, filename=output_path)
