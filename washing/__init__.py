from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_washing():
    result = "出錯"
    try:
        driver = webdriver.Safari()
        driver.get('http://monitor.isesa.com.tw/monitor/?code=yJL1OU')
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table[@id='tb_machineList1']/tbody"))
            )
        finally:
            pass

        html = element.get_attribute('outerHTML')
        table = BeautifulSoup(html, 'html.parser')
        count = 0
        avalible = []
        unavalible = []
        temp = {}

        for i in table.select("tr span"):
            if i.text:
                if i.text.startswith("1D"):
                    count = 0
                    continue
            match(count):
                case 0:
                    pass
                case 1:
                    temp["name"] = i.text
                case 2:
                    temp["status"] = i.text
                case 3:
                    temp["how many time"] = i.text
                    if temp["status"] == "運轉中":
                        unavalible.append(temp)
                    else:
                        avalible.append(temp)
                    temp = {}
            if count >= 3:
                count = 0
            else:
                count += 1
        result = f"目前有{len(avalible)}台洗衣機可用、{len(unavalible)}台不可用。\n詳細資訊如下：\n  可用：\n"
        for i in avalible:
            result += f"    {i['name']}\n"
        result += " 不可用\n"
        for i in unavalible:
            result += f"    {i['name']} 開始時間：{i['how many time']}\n"
        return result
    except:
        return result