import re
from mods.mysql_add import insert_data
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

options = Options()
#禁用 Chrome 瀏覽器中的自動化控制功能，這可以防止網站檢測到你正在使用自動化工具
options.add_argument("--disable-blink-features=AutomationControlled")
#禁用 Chrome 瀏覽器的資訊欄，這樣就不會顯示任何提示訊息或警告
options.add_argument("--disable-infobars")
#禁用 Chrome 瀏覽器的擴展程式，以確保瀏覽器在自動化過程中不受到擴展程式的影響
options.add_argument("--disable-extensions")
#禁用 Chrome 瀏覽器的彈出視窗阻擋功能，以確保在瀏覽過程中不會被阻止任何彈出視窗
options.add_argument("--disable-popup-blocking")
#它模擬了一個 Windows 10 下的 Chrome 瀏覽器訪問網頁的信息，這有助於在訪問網站時隱藏自動化的痕跡，使其看起來更像是由真實使用者訪問的
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")

#這是一個管理 Chrome WebDriver 下載和安裝的工具。通過呼叫 install() 方法，它會自動下載並安裝適用於您的作業系統的 Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

wait = WebDriverWait(driver, 10)
#--------------------------------------------------------
#此段為進入買房頁面並點擊住宅

url = "https://www.hbhousing.com.tw/BuyHouse/%E5%8F%B0%E5%8C%97%E5%B8%82/116"
driver.get(url)
time.sleep(5)
q6 = driver.find_element(By.CSS_SELECTOR, 'input[name="q6"][value="1"]')
q6.click()
time.sleep(5)

#---------------------------------------------------------
#此段為確認最大頁數

max_page = driver.find_element(By.XPATH,"//*[@id='tab01']/ul/li[8]")
a = int(max_page.text)
print(max_page.text)

#---------------------------------------------------------
#設定點擊次數，為了對應最大頁數
clicked_count = 0
#所有資料的陣列
data_all_last=[]
#設定目前頁面資料爬了幾次
c = int(0)
#---------------------------------------------------------
#第一段 迴圈是要跑全部頁數
while clicked_count < int(a)+1:
    #這邊抓取物件編號，因為比較穩定 elements抓取class_name相同的所有資料
    parent_elements = driver.find_elements(By.CLASS_NAME,"item__main")
    #目前頁面資料比數
    data_list = len(parent_elements)

    #-----------------------------------------------------
    #此迴圈是在判斷是要下一頁還是點擊元素
    for parent_element in parent_elements:

        if c == data_list:
            next = driver.find_element(By.XPATH, "//a[contains(text(), '>')]")
            next.click()
            c = int(0)
            clicked_count +=1 
            time.sleep(5)
            break
        else:
            c+=1
            data =  parent_element.find_element(By.CSS_SELECTOR, "a")
            action = ActionChains(driver)
            action.move_to_element(data).click().perform()
    #--------------------------------------------------------    
                

       #切換網頁
        time.sleep(2)
        # 切换到新頁面
        new_window = driver.window_handles[1]
        #將 WebDriver 的控制權轉移到新打開的窗口
        driver.switch_to.window(new_window)
        #讀取網頁
        new_page_html = driver.page_source
        #這是抓取單一物件的相關資訊的陣列
        data_all = []
        time.sleep(1)
        
        #soup = BeautifulSoup(new_page_html, 'html.parser')
        #這裡使用WebDriverWait來等待元素出現最多等10秒，
        #當元素出現時就可以直接執行抓取元素。只抓取設定的值，以確保網頁有跑出來
        element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.hightlightprice'))
    )
        #用BeautifulSoup抓取網頁全部的資訊
        soup = BeautifulSoup(new_page_html, 'html.parser')
        #把金錢的text後面加萬
        price_with_unit = str(element.text.strip()) + "萬"
        #把資料加到data_all的陣列
        data_all.append(price_with_unit)
        #----------------------------------------------------
        #以陣列的方式使用迴圈抓取多筆資料
        address_data = ["item_name","item_add"]
        for name in address_data:
            #------------------------------------------------
            #這個try是用來確認資造勢不是空值，是空值回傳異常資訊並跳過往下一筆資料執行
            try:
                name_data = soup.find("p", class_=name)
                if name_data is not None:
                    name = name_data.text.strip()

                    data_all.append(name)
                else:
                    raise ValueError("文本为空")
            except ValueError as ve:
                # 处理空文本的异常情况
                print("发现空文本:", ve)
                pass
            except Exception as e:
                # 处理其他异常情况
                print("发生异常:", e)
                pass
            #---------------------------------------------------
        #-------------------------------------------------------
        #以陣列的方式使用迴圈抓取多筆資料，這邊是抓表單所以抓取特定的資料
        all_data = ['建物面積','屋齡','樓層','車位']
        for cm in all_data:
            Building_area_data = soup.find('td', string =cm)
            #抓取這邊all_data裡面的兄弟元素底下的文字
            if Building_area_data:
                building_area_value = Building_area_data.find_next_sibling('td')
                #------------------------------------------------
                #有些資料後面還有按鈕，這裡是把按鈕給清掉
                button_element = building_area_value.find('button')
                if button_element:
                    button_element.decompose()
                #------------------------------------------------
                #把資料加入data_all
                data_all.append(building_area_value.text.strip())
        #把data_all裡面的資料加入data_all_last來確保每一筆相關資料都在同一陣列裡面
        data_all_last.append(data_all) 
        #關閉當前頁面
        driver.close()
        #切換回主頁面
        driver.switch_to.window(driver.window_handles[0])
        #--------------------------------------------------------- 
    #讀取主頁面的資訊
    page_html = driver.page_source
    #try:
    #    page = driver.find_element(By.CLASS_NAME,"house__list__pagenum")
    #    page.find_element(By.XPATH, "//a[text()='>']").click
    #except NoSuchElementException:
    #    break
#-------------------------------------------------------------------
#進行把資料匯入mysql並告知新增幾筆資料
inserted_count = insert_data(data_all_last)
print("插入了 {} 条新数据".format(inserted_count))
#-------------------------------------------------------------------

