from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time
import csv
import datetime
import threading
def scroll(driver, url):

    driver.get(url)
    driver.execute_script(f"window.scrollBy(0, 5000);")
    times = 0
    while True:
        
    
        # 滾動頁面像素
        scroll_increment = 1
        driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
        
        # 設定滾動次數
        if times == 60000:
            break  
        else:
            
            times += 1
            continue  
def get_104(driver):
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        all_openings = []

        for find_element in soup.find_all("article", class_="b-block--top-bord job-list-item b-clearfix js-job-item"):
            # 公司名
            company = find_element.get('data-cust-name', None)
            
            # 職稱
            title_element = find_element.find("a", {"data-qa-id": "jobSeachResultTitle"})
            title = title_element.text.strip() if title_element else None
            
            # 技能
            job_element = find_element.find("p", class_="job-list-item__info b-clearfix b-content")
            job = job_element.text.strip() if job_element else None
            
            # 薪資待遇
            if find_element.find("span", class_="b-tag--default") is  None:
                salary_element = find_element.find("a", class_="b-tag--default")
                salary = salary_element.text.strip() 
            else:
                
                salary = ("待遇面議")

            
            
            # 將提取的資訊添加到列表中
            all_openings.append({"公司": company, "職稱": title, "工作內容": job, "薪資": salary})

        return all_openings
    except TimeoutException:
        print("等待元素時間過長。")
        return []
    except Exception as e:
        print(f"抓取過程出現問題：{e}")
        return []
    finally:
        print("MISSION COMPLETE!!")
def click_button(driver):
    try:
        # 等待按鈕出現
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "js-more-page"))
        )
        # 點擊按鈕
        button.click()
        print("按鈕已點擊")
    except Exception as e:
        print(f"點擊按鈕時出錯: {e}")
# 初始化webdriver
options = webdriver.ChromeOptions()
# 添加其他需要的選項
driver = webdriver.Chrome(options=options)

url = ("https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword=%E6%A9%9F%\
       E5%99%A8%E5%AD%B8%E7%BF%92%E5%B7%A5%E7%A8%8B%E5%B8%AB&expansionType=area%\
       2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&area=6001001000&order=14&asc=0&page=1&mode=s&jobsource=index_s&langFlag=0&langStatus=0&recommendJob=1&hotJob=1")
driver.get(url)
time.sleep(5)

scroll(driver, url)
thread = threading.Thread(target=click_button, args=(driver,))
thread.start()
thread.join()
jobs = get_104(driver)
time.sleep(3)
# 寫入CSV
with open('crawl_104.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # 寫入一個包含今日日期的單獨行
    today_date = datetime.date.today()
    writer.writerow(['今日日期', today_date])
    
    # 再創建一個DictWriter來寫入職位資訊
    fieldnames = ["公司", "職稱", "工作內容", "薪資"]
    dict_writer = csv.DictWriter(file, fieldnames=fieldnames)
    dict_writer.writeheader()
    
    # 寫入職位資訊
    for job in jobs:
        dict_writer.writerow(job)

driver.quit()