import os
import json
import requests
from bs4 import BeautifulSoup

from dotenv import load_dotenv
load_dotenv()

def nearest_weather(lot, lat): # 利用經緯度算出最近的測站
    msg = "出錯"
    try:
        nearest_distance = 10000
        code = os.getenv('GOV_AUTH')
        data = requests.get(f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization={code}&format=JSON')
        jsondata = data.json()
        location = jsondata['records']['location']
        position = {}
        for i in location:
            lat_change = (lat - float(i['lat'])) **2 # 利用畢氏定理 a^2 + b^2 = c^2 算出直線距離
            lot_change = (lot - float(i['lon'])) **2
            distance = (lat_change + lot_change) **0.5
            if distance < nearest_distance: # 如果已知的最短距離小於新計算出的數值，就更新最短距離
                nearest_distance = distance
                position = i
        data = requests.get(f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization={code}&format=JSON')
        jsondata = data.json()
        location = jsondata['records']['location']
        for i in location:
            lat_change = (lat - float(i['lat'])) **2 # 利用畢氏定理 a^2 + b^2 = c^2 算出直線距離
            lot_change = (lot - float(i['lon'])) **2
            distance = (lat_change + lot_change) **0.5
            if distance < nearest_distance: # 如果已知的最短距離小於新計算出的數值，就更新最短距離
                nearest_distance = distance
                position = i
        temp = position['weatherElement'][3]['elementValue']
        humid = position['weatherElement'][4]['elementValue']
        msg = f"離您最近的測站是{position['locationName']}。\n\n目前觀測數據是：\n溫度：{temp}\n濕度：{humid}"
        return msg
    except Exception as e:
        return msg

def forecast(address):
    area_list = {}
    # 將主要縣市個別的 JSON 代碼列出
    json_api = {"宜蘭縣":"F-D0047-001","桃園市":"F-D0047-005","新竹縣":"F-D0047-009","苗栗縣":"F-D0047-013",
            "彰化縣":"F-D0047-017","南投縣":"F-D0047-021","雲林縣":"F-D0047-025","嘉義縣":"F-D0047-029",
            "屏東縣":"F-D0047-033","臺東縣":"F-D0047-037","花蓮縣":"F-D0047-041","澎湖縣":"F-D0047-045",
            "基隆市":"F-D0047-049","新竹市":"F-D0047-053","嘉義市":"F-D0047-057","臺北市":"F-D0047-061",
            "高雄市":"F-D0047-065","新北市":"F-D0047-069","臺中市":"F-D0047-073","臺南市":"F-D0047-077",
            "連江縣":"F-D0047-081","金門縣":"F-D0047-085"}
    msg = '找不到天氣預報資訊。'    # 預設回傳訊息
    try:
        code = 'CWB-C26ED602-B0F7-49E1-A71C-28D88906ACAD'
        url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={code}&downloadType=WEB&format=JSON'
        f_data = requests.get(url)   # 取得主要縣市預報資料
        f_data_json = f_data.json()  # json 格式化訊息內容
        location = f_data_json['records']['location']  # 取得縣市的預報內容
        for i in location:
            city = i['locationName']    # 縣市名稱
            wx8 = i['weatherElement'][0]['time'][0]['parameter']['parameterName']    # 天氣現象
            mint8 = i['weatherElement'][1]['time'][0]['parameter']['parameterName']  # 最低溫
            maxt8 = i['weatherElement'][2]['time'][0]['parameter']['parameterName']  # 最高溫
            ci8 = i['weatherElement'][2]['time'][0]['parameter']['parameterName']    # 舒適度
            pop8 = i['weatherElement'][2]['time'][0]['parameter']['parameterName']   # 降雨機率
            area_list[city] = f'未來 8 小時{wx8}，最高溫 {maxt8} 度，最低溫 {mint8} 度，降雨機率 {pop8} %'  # 組合成回傳的訊息，存在以縣市名稱為 key 的字典檔裡
        for i in area_list:
            if i in address:        # 如果使用者的地址包含縣市名稱
                msg = area_list[i]  # 將 msg 換成對應的預報資訊
                # 將進一步的預報網址換成對應的預報網址
                url = f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/{json_api[i]}?Authorization={code}&elementName=WeatherDescription'
                f_data = requests.get(url)  # 取得主要縣市裡各個區域鄉鎮的氣象預報
                f_data_json = f_data.json() # json 格式化訊息內容
                location = f_data_json['records']['locations'][0]['location']    # 取得預報內容
                break
        for i in location:
            city = i['locationName']   # 取得縣市名稱
            wd = i['weatherElement'][0]['time'][1]['elementValue'][0]['value']  # 綜合描述
            if city in address:           # 如果使用者的地址包含鄉鎮區域名稱
                msg = f'未來八小時天氣{wd}' # 將 msg 換成對應的預報資訊
                break
        return msg  # 回傳 msg
    except Exception as e:
        return msg  # 如果取資料有發生錯誤，直接回傳 msg