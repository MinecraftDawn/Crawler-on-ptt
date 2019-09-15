import re
import os
import time
import requests
import threading
from bs4 import BeautifulSoup

root = "https://www.ptt.cc"

# 取得最新頁數
newest = root + "/bbs/Beauty/index.html"
# 設定cookie
cookie_over18 = {"over18":'1'}
# http header
http_header = {'Connection':'close'}
# 目錄資料夾位置
dirPath = "images/"

"""
找出最新頁面的url
"""
def findNewestPage():
    # 取得最新頁數的respond
    resNewest = requests.get(newest, cookies=cookie_over18, headers=http_header)
    # 解析html
    soup = BeautifulSoup(resNewest.text, "html.parser")
    # 取得所有btn wide物件
    preBtn = soup.find_all("a", class_="btn wide")
    for btn in preBtn:
        # 若文字是"‹ 上頁"，則回傳網址頁數
        if btn.text == "‹ 上頁":
            tailUrl = btn['href'].split('/')[-1]
            return int(tailUrl[5:tailUrl.find('.')])

"""
下載圖片
"""
def downloadImage(imageUrl:str) ->None:
    # 取得檔案名稱
    fileName = imageUrl.split('/')[-1]
    # 發送請求，取得檔案資料
    try:
        imgRes = requests.get(imageUrl, headers=http_header)
        #若資料夾不存在，則創建資料夾
        if not os.path.exists(dirPath):
            os.mkdir(dirPath)
        # 設定檔案路徑及檔名
        filePath = dirPath + fileName
        while os.path.exists(filePath):
            fileName = '_' + fileName
            filePath = dirPath + fileName
        # 創建檔案
        with open(filePath, 'bw') as image:
            image.write(imgRes.content)
    except IOError as e:
        print(e)
    except requests.exceptions.RequestException as e:
        print(e)

# 從最新頁(數字最大)迭代到第一頁
start = findNewestPage()
try:
    with open("page.ini", "r") as pageFile:
        start = int(pageFile.read())
except FileNotFoundError:
    pass
except TypeError:
    print("page.ini content error")
    
for page in range(start,0,-1):
    # 設定主頁面網址
    url = root + "/bbs/Beauty/index" + str(page) +".html"
    # 取得頁面respond
    respond = requests.get(url, cookies=cookie_over18, headers=http_header)
    # 解析主頁html
    soup = BeautifulSoup(respond.text, "html.parser")
    # 取得頁面文章
    titles = soup.find_all("div", class_="title")
    
    for title in titles:
        # 若該div未有連結
        if not title.a: continue
        # 取得文章連結
        artiUrl = root + title.a["href"]
        # 取得文章respond
        artiRes = requests.get(artiUrl, cookies=cookie_over18, headers=http_header)
        # 解析文章html
        artiSoup = BeautifulSoup(artiRes.text , "html.parser")
        # 找到主要div
        mainDiv = artiSoup.find("div", id="main-content")
        # 若未找到則繼續
        if not mainDiv: continue
        # 找到全部的連結
        for link in mainDiv.find_all("a"):
            # 取得連結網址
            imageUrl = link["href"]
            # 判斷檔案是否符合格式
            if re.match("http[s]?://(\S)*\.(jpg|png|gif)$", imageUrl):
                # 若為https，則轉換成http
                if imageUrl[4] == 's':
                    imageUrl = imageUrl[:4] + imageUrl[5:]
                # 避免過多執行緒
                while threading.active_count() > 30:
                    print("目前執行緒數量： " + str(threading.active_count()))
                    time.sleep(5)
                # 新增執行緒下載圖片
                thread = threading.Thread(target=downloadImage,args=(imageUrl,))
                thread.start()
                
    # 開啟檔案，用來儲存下載頁數
    with open("page.ini", "w") as pageFile:
        pageFile.write(str(page))
