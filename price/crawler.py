import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# 记录开始时间
start_time = time.time()

# 读取 test.xlsx 文件
df = pd.read_excel('link.xlsx')

# 获取第二列的 URL 列表
url_list = df.iloc[:, 1].tolist()
print(url_list)

# chromedriver 路径
# chromedriver_path = r"chromedriver.exe"

# 配置浏览器选项
options = Options()
options.add_argument("--start-maximized")
options.add_argument('--blink-settings=imagesEnabled=false')

# 创建 WebDriver 服务
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 打开亚马逊首页
driver.get("https://www.amazon.it")
input("按回车进入下一步")

# 用于存储每个商品的价格
title_list = []
tag_list = []
price_list = []
discount_list = []

# 爬取函数
def crawl(url):
    price_value = ""
    discount_text = ""
    deal_text = ""
    title_text = ""
    if url == 'https://www.amazon.it/dp/?psc=1':
        price_list.append(price_value)  # 将每个商品的价格添加到列表中
        discount_list.append(discount_text)  # 将每个商品的折扣添加到列表中
        title_list.append(title_text)  # 将每个商品的标题添加到列表中
        tag_list.append(deal_text)  # 将每个商品的tag添加到列表中
    else:
        for i in range(5):
            try:
                driver.get(url)
                # 尝试通过 XPath 定位到 productTitle 的第一个 span 元素
                title_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '(//span[@id="productTitle"])[1]'))
                )
                title_text = title_element.text

                if title_text:  # 如果找到了标题
                    print(f"已进入目标商品页面：{url}")
                    print("找到的 productTitle 文本：", title_text)
                    break
            except:
                print("网页状态异常，正在重试")
                time.sleep(2)

        try:
            # 尝试通过 XPath 定位到价格元素
            price_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="priceValue"]'))
            )
            price_value = price_element.get_attribute('value')

            if price_value:  # 如果找到了价格
                print("找到的价格值：", price_value)
            else:
                price_value = ""
                print("未找到价格字段")
        except Exception as e:
            # 如果没有找到元素，捕获异常并设置价格为 "未找到"
            price_value = ""
            print(f"出现错误: {e}, 未找到价格字段")

        try:
            # 尝试通过 XPath 定位到折扣元素
            dis_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '(//span[@aria-hidden="true" and contains(@class, "savingsPercentage")])[1]'))
            )
            discount_text = dis_element.text

            if discount_text:  # 如果找到了折扣
                print("找到的折扣值：", discount_text)
            else:
                discount_text = ""
                print("未找到折扣字段")
        except Exception as e:
            # 如果没有找到元素，捕获异常并设置折扣为 "未找到"
            discount_text = ""
            print(f"未找到折扣字段")

        try:
            # 尝试通过 XPath 定位到 dealBadgeSupportingText 的 span 元素
            deal_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//span[@id="dealBadgeSupportingText"]'))
            )
            deal_text = deal_element.text

            if deal_text:  # 如果找到了文本
                print("找到的deal tag：", deal_text)
            else:
                deal_text = ""
                print("未找到deal tag")
        except Exception as e:
            # 如果没有找到元素，捕获异常并设置为空
            deal_text = ""
            print("未找到deal tag")

        price_list.append(price_value)  # 将每个商品的价格添加到列表中
        discount_list.append(discount_text)  # 将每个商品的折扣添加到列表中
        title_list.append(title_text)  # 将每个商品的标题添加到列表中
        tag_list.append(deal_text)  # 将每个商品的tag添加到列表中

# 遍历所有的 URL 并爬取数据
for index, url in enumerate(url_list, start=1):  # 从1开始计数
    print(f"爬取第{index}条: {url}")
    crawl(url)
    if index == 30:
        time.sleep(60)

# 将价格列表添加到原始 DataFrame
df['title'] = title_list
df['price'] = price_list
df['discount'] = discount_list
df['tag'] = tag_list

# 将结果保存为新的 CSV 文件
df.to_csv('price.csv', index=False, encoding='utf-8-sig')

print("已将结果保存为 price.csv 文件")

# 记录结束时间
end_time = time.time()

# 计算总耗时
elapsed_time = end_time - start_time
print(f"任务完成，总耗时: {elapsed_time:.2f} 秒")

# 关闭浏览器
driver.quit()
