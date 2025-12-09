import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import sys
from selenium.webdriver.common.action_chains import ActionChains
import os
import pyperclip
from selenium.webdriver.common.keys import Keys
import platform


# ------------------------UI------------------------
# 创建主窗口
root = tk.Tk()
root.title("选择站点")
root.geometry("250x250")

# 可选国家及对应代码
options = {
    "英国": "UK",
    "意大利": "IT",
    "德国": "DE",
    "法国": "FR",
    "西班牙": "ES"
}

# 用于保存选中状态的变量
vars_dict = {name: tk.BooleanVar() for name in options}

# 创建多选框
for i, name in enumerate(options):
    tk.Checkbutton(root, text=name, variable=vars_dict[name]).pack(anchor='w')

# 无头浏览器选项
headless_var = tk.BooleanVar(value=False)  # 默认不启用
tk.Checkbutton(root, text="启用无头浏览器", variable=headless_var).pack(anchor='w', pady=10)

# 按钮回调函数
def confirm_selection():
    global country_list
    global x  # 控制无头浏览器
    country_list = [code for name, code in options.items() if vars_dict[name].get()]
    if not country_list:
        messagebox.showwarning("提示", "请至少选择一个国家")
        return
    x = headless_var.get()
    print("已选择国家代码：", country_list)
    root.destroy()  # 关闭窗口

# 绑定右上角叉号关闭事件
def on_close():
    print("用户取消选择，程序退出")
    sys.exit()

root.protocol("WM_DELETE_WINDOW", on_close)

# 确认按钮
tk.Button(root, text="确定", command=confirm_selection).pack(pady=20)

# 启动主循环
root.mainloop()

# 记录开始时间
start_time = time.time()

country_file_map = {
    "UK": "UKAsin.xlsx",
    "IT": "ITAsin.xlsx",
    "DE": "DEAsin.xlsx",
    "FR": "FRAsin.xlsx",
    "ES": "ESAsin.xlsx"
}

def CountryAsin(clist):
    asin_dict = {}  # 用字典存每个国家的 ASIN 列表
    for country in clist:
        df = pd.read_excel(f'Asin/{country}Asin.xlsx')
        asin_list = df.iloc[:, 0].tolist()
        asin_str = ",".join(f'"{asin}"' for asin in asin_list)
        asin_dict[country] = asin_str
    return asin_dict

asin_dict = CountryAsin(country_list)

# chromedriver 路径
chromedriver_path = r"chromedriver.exe"

# 配置浏览器选项
options = Options()
if x:
    options.add_argument("--headless")
options.add_argument("--start-maximized")
options.add_argument('--blink-settings=imagesEnabled=false')
prefs = {
    "download.default_directory": "download",     # 默认下载路径
    "download.prompt_for_download": False,        # 不弹出下载对话框
    "download.directory_upgrade": True,           # 自动覆盖老目录
    "safebrowsing.enabled": True                  # 允许下载
}
options.add_experimental_option("prefs", prefs)
# 创建 WebDriver 服务
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

# 打开卖家精灵，自动跳转登陆页面
# 参数设置
url = f"https://www.sellersprite.com/v3/competitor-lookup?market=IT&monthName=bsr_sales_nearly&asins=%5B{list(asin_dict.values())[0]}%5D&page=1&nodeIdPaths=%5B%5D&symbolFlag=false&size=100&order%5Bfield%5D=amz_unit&order%5Bdesc%5D=true&lowPrice=N"
for attempt in range(1, 5 + 1):
    try:
        driver.get(url)
        print(f"第 {attempt} 次尝试加载成功：{url}")
        break  # 成功加载后跳出循环
    except Exception as e:
        print(f"第 {attempt} 次加载失败：{e}")
        if attempt < 5:
            print(f"5 秒后重试第 {attempt + 1} 次...")
            time.sleep(5)
        else:
            print("超过最大重试次数，停止尝试。")
            sys.exit()

# ======开始模拟键鼠操作======
wait = WebDriverWait(driver, 10)

# ------------------------读取账密------------------------
# 构造文件路径
file_path = os.path.join("Ap.txt")  # 同级文件夹下的 Ap.txt

# 打开文件并读取前两行
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()
    account = lines[0].strip()  # 第一行去掉换行符
    pw = lines[1].strip()       # 第二行去掉换行符

print("账号:", account)
print("密码:", pw)

# ------------------------登录------------------------
# 点击账号登录
print("正在登陆")
account_tab = wait.until(
    EC.element_to_be_clickable((By.XPATH, '//a[@class="nav-link" and @href="#pills-account"]'))
)
account_tab.click()
# 输入账号
time.sleep(0.5)
email_input = wait.until(
    EC.presence_of_element_located((By.XPATH, "(//input[@name='email'])[2]"))
)
email_input.click()
email_input = wait.until(
    EC.presence_of_element_located((By.XPATH, "(//input[@name='email'])[2]"))
)
email_input.send_keys(account)
# 输入密码
time.sleep(0.5)
password_input = wait.until(
    EC.presence_of_element_located((By.XPATH, "(//input[@type='password'])[2]"))
)
password_input.click()
password_input = wait.until(
    EC.presence_of_element_located((By.XPATH, "(//input[@type='password'])[2]"))
)
password_input.send_keys(pw)
# 点击登录
time.sleep(0.5)
login_buttons = wait.until(
    EC.presence_of_all_elements_located((By.XPATH, "//button[contains(@class, 'login-btn')]"))
)
login_buttons[1].click()
'''
# ------------------------通过asin搜索------------------------
# 等待元素加载
asin_input = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//input[@placeholder='父(子)体ASIN或产品链接，如 B00FLYWNYQ']")
    )
)
# 滚动到元素可见
driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", asin_input)
# 点击激活输入框
asin_input.click()
# 输入变量
pyperclip.copy(asin_str)
# 根据系统选择粘贴快捷键
if platform.system() == "Darwin":  # macOS
    asin_input.send_keys(Keys.COMMAND, 'v')
else:  # Windows / Linux
    asin_input.send_keys(Keys.CONTROL, 'v')
time.sleep(0.5)
# 点击立即查询
# 等待按钮可点击
search_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[@data-v-f53055e6 and contains(@class,'el-button--primary')]")
    )
)
search_button.click()'''
# ------------------------爬取需要的数据------------------------
def exeByCountry(country):
    asins = []
    bsr_a = []
    bsr_b = []
    bsr_c = []
    so_father = []
    soGrothRate = []
    Rev = []
    so_son = []
    soRev = []
    price = []

    def getData():
        # 1.获取Asin
        # 等待页面中出现含有“ASIN:”的元素
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//span[text()="ASIN:"]'))
        )
        # 找到所有 <span>ASIN:</span> 元素
        spans = driver.find_elements(By.XPATH, '//span[text()="ASIN:"]')
        for span in spans:
            # 获取父节点（通常是 <div>）
            parent_div = span.find_element(By.XPATH, './..')
            # 获取父节点的完整文本内容，例如 "ASIN: B0CF5ZQH7Y 查看详情"
            full_text = parent_div.text.strip()
            # 提取 ASIN 号部分（去掉 “ASIN:” 和其他文字）
            # 注意：根据网页结构，你可以调整这部分提取逻辑
            if "ASIN:" in full_text:
                asin_text = full_text.split("ASIN:")[-1].split()[0].strip()
                asins.append(asin_text)
        print(asins)

        # 2.获取大类BSR
        # 等待 td 元素加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//td[contains(@class, "el-table_1_column_5")]'))
        )
        tds = driver.find_elements(By.XPATH, '//td[contains(@class, "el-table_1_column_5")]')
        for td in tds:
            # a: border-bt 内文本
            try:
                a = td.find_element(By.XPATH, './/div[contains(@class, "border-bt")]').text.strip()
            except:
                a = ""
            # 找出 td 中所有的 span.text-danger
            spans = td.find_elements(By.XPATH, './/span[contains(@class, "text-danger")]')
            # b 和 c 分别取第 1、2 个
            b = spans[0].text.strip() if len(spans) >= 1 else ""
            c = spans[1].text.strip() if len(spans) >= 2 else ""
            bsr_a.append(a)
            bsr_b.append(b)
            bsr_c.append(c)
        print("sbr1:", bsr_a)
        print("sbr2:", bsr_b)
        print("sbr3:", bsr_c)

        # 获取销量、增长率
        # 获取所有目标 td
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td.el-table_1_column_7.is-center'))
        )
        td_elements = driver.find_elements(By.CSS_SELECTOR, 'td.el-table_1_column_7.is-center')
        for td in td_elements:
            try:
                # 获取 class="border-bt" 下的 div 文本
                a_div = td.find_element(By.CSS_SELECTOR, 'div.border-bt')
                a_text = a_div.text.strip()
            except:
                a_text = ""
            try:
                # 获取 class="text-muted" 下的 div 文本
                b_div = td.find_element(By.CSS_SELECTOR, 'div.text-muted')
                b_text = b_div.text.strip()
            except:
                b_text = ""
            so_father.append(a_text)
            soGrothRate.append(b_text)
        print("销量：", so_father)
        print("销量增长率：", soGrothRate)

        # 获取销售额
        # 获取所有目标 td
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td.el-table_1_column_8.is-center'))
        )
        td_elements = driver.find_elements(By.CSS_SELECTOR, 'td.el-table_1_column_8.is-center')
        # 提取文本
        Rev_elements = [td.text.strip() if td.text.strip() else "" for td in td_elements]
        Rev.extend(Rev_elements)
        # 输出结果
        print("销售额：", Rev)

        # 获取子体销量、增长率
        # 获取所有目标 td 元素
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td.el-table_1_column_9.is-center'))
        )
        td_elements = driver.find_elements(By.CSS_SELECTOR, 'td.el-table_1_column_9.is-center')
        # 遍历每个 td
        for td in td_elements:
            try:
                # 获取 <span class="border-bt"> 中的文本
                span_text = td.find_element(By.CSS_SELECTOR, 'span.border-bt').text.strip()
            except:
                span_text = ""

            try:
                # 获取 <div class="text-muted"> 中的文本
                muted_text = td.find_element(By.CSS_SELECTOR, 'div.text-muted').text.strip()
            except:
                muted_text = ""

            so_son.append(span_text)
            soRev.append(muted_text)
        # 打印结果
        print("子体销量：", so_son)
        print("子体销售额：", soRev)

        # 价格
        # 获取所有目标 td 元素
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td.el-table_1_column_11.is-center'))
        )
        td_elements = driver.find_elements(By.CSS_SELECTOR, 'td.el-table_1_column_11.is-center')
        # 提取每个 td 中 border-bt 的文本
        for td in td_elements:
            try:
                text = td.find_element(By.CSS_SELECTOR, 'div.border-bt').text.strip()
            except:
                text = ""
            price.append(text)
        # 打印结果
        print("价格：", price)

    #
    page = 1  # 从第 1 页开始
    while True:

        url1 = f"https://www.sellersprite.com/v3/competitor-lookup?market={country}&monthName=bsr_sales_nearly&asins=%5B{asin_dict.get(country, "")}%5D&page={page}&nodeIdPaths=%5B%5D&symbolFlag=false&size=100&order%5Bfield%5D=amz_unit&order%5Bdesc%5D=true&lowPrice=N"
        print(f"正在加载第 {page} 页：{url1}")
        for attempt in range(1, 5 + 1):
            try:
                driver.get(url1)
                print(f"第 {attempt} 次尝试加载成功：{url1}")
                break  # 成功加载后跳出循环
            except Exception as e:
                print(f"第 {attempt} 次加载失败：{e}")
                if attempt < 5:
                    print(f"5 秒后重试第 {attempt + 1} 次...")
                    time.sleep(5)
                else:
                    print("超过最大重试次数，停止尝试。")
                    sys.exit()

        # 等待页面加载完成
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.content.cn"))
            )
        except:
            print(f"第 {page} 页加载超时，停止循环。")
            break

        # 检查是否有“很抱歉，暂无结果！”提示
        content_div = driver.find_element(By.CSS_SELECTOR, "div.content.cn")
        if "很抱歉，暂无结果！" in content_div.text:
            print(f"第 {page} 页没有数据，停止循环。")
            break

        # 调用getData()抓取数据
        getData()
        page += 1  # 翻页

    data = {
        "ASIN": asins,
        "大类BSR排名": bsr_a,
        "7日BSR增长数": bsr_b,
        "7日BSR增长率": bsr_c,
        "销量（父）": so_father,
        "增长率": soGrothRate,
        "父体销售额": Rev,
        "子体销量": so_son,
        "子体销售额": soRev,
        "价格": price
    }

    # 使用 pd.DataFrame 构建表格
    df = pd.DataFrame(data)
    df.replace("-", "", inplace=True)
    # 获取当前时间，格式化为 YYYYMMDD_HHMMSS
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 确保 download 文件夹存在
    if not os.path.exists("download"):
        os.makedirs("download")

    filename = os.path.join("download", f"{country}_{now}.csv")
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"任务完成，已导出{filename}")

for i in country_list:
    exeByCountry(i)

# 记录结束时间
end_time = time.time()
# 计算总耗时
elapsed_time = end_time - start_time
print(f"总耗时: {elapsed_time:.2f} 秒")
# 关闭浏览器
driver.quit()
