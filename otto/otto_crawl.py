from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  # 用于自动安装和管理 chromedriver
import pandas as pd
import time
import sys
import datetime

# 读取links文件
# 读取 Excel 文件
file_path = "links.xlsx"
df = pd.read_excel(file_path)

# 获取第一列的数据
links_list = df.iloc[:, 0].tolist()

# 设置 Chrome WebDriver
options = webdriver.ChromeOptions()

# 可以选择启用无头模式（如果不需要打开浏览器界面）
options.add_argument('--headless')  # 如果想在后台运行，可以取消注释这一行

# 使用 WebDriver Manager 自动管理 chromedriver
service = Service(ChromeDriverManager().install())

# 启动 Chrome 浏览器
driver = webdriver.Chrome(service=service, options=options)

# 初始化列表
product_name_li = []
product_price_li = []
availability_message_li = []
product_article_number_li = []

# 测试网络环境
print("测试网络环境")
driver.get("https://www.otto.de/p/tcl-85c803gx1-mini-led-fernseher-214-cm-85-zoll-4k-ultra-hd-android-tv-google-tv-smart-tv-1850851342/?artNr=46761905")
try:
    # 显式等待直到页面加载完成
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))  # 确保页面的 body 元素加载完成
    )
    # 查找 class="error-page_message" 的 main 元素
    error_messages = driver.find_elements(By.CSS_SELECTOR, "main.error-page_message")
    if error_messages:
        print("网络错误或页面异常")
        driver.quit()
        sys.exit()

except Exception as e:
    print("网络可用")

# 显式等待页面中指定元素的出现
def scraper(url):
    print(f"正在进入：{url}")
    driver.get(url)
    product_name = ""
    product_price = ""
    availability_message = ""
    product_article_number = ""  # 默认赋值为空值

    try:
        # 获取产品名称
        product_name_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pdp_short-info__main-name"))
        )
        product_name = product_name_element.text
        print("产品名称：", product_name)

    except Exception as e:
        print("无法找到产品名称:", e)

    try:
        # 获取产品价格
        product_price_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "js_pdp_price__retail-price__value_"))
        )
        product_price = product_price_element.text
        print("产品价格：", product_price)

    except Exception as e:
        print("无法找到产品价格:", e)

    try:
        # 获取可用性信息
        availability_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "js_availabilityMessage_Feature"))
        )
        availability_message = availability_element.text
        print("可用性信息：", availability_message)

    except Exception as e:
        try:
            availability_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pdp_delivery__soldout-message.oc-headline-50"))
            )
            availability_message = availability_element.text
            print("可用性信息：", availability_message)
        except Exception as e:
            print("无法找到可用性信息:", e)

    try:
        # 获取产品编号
        article_number_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pdp_article-number"))
        )
        product_article_number = article_number_element.text
        try:
            product_article_number = product_article_number.replace("Artikel-Nr. ", "")
        except Exception as e:
            print("产品编号无法去除Artikel-Nr. ")
        print("产品编号：", product_article_number)

    except Exception as e:
        print("无法找到产品编号:", e)

    product_name_li.append(product_name)
    product_price_li.append(product_price)
    availability_message_li.append(availability_message)
    product_article_number_li.append(product_article_number)


for i, link in enumerate(links_list):
    scraper(link)

    # 每50个循环休息1分钟
    if (i + 1) % 50 == 0:
        print("休息 1 分钟...")
        time.sleep(60)

# 关闭浏览器
driver.quit()

# 导出信息
data = {
    'product': product_name_li,
    'price': product_price_li,
    'availability': availability_message_li,
    'article_number': product_article_number_li,
    'link': links_list
}

df = pd.DataFrame(data)

# 导出为 Excel 文件
current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d-%H-%M-%S")
# 使用当前时间作为文件名
output_file = f"{formatted_time}.xlsx"
df.to_excel(output_file, index=False)
print(f"数据已导出到 {output_file}")