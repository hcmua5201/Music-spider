import time
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
import os

# 自动化获取浏览器cookies
driver = webdriver.Chrome()
driver.get("http://music.2t58.com/")
# 打印浏览器cookies
cookies = driver.get_cookies()
# 转为json格式
cookies_json = {}
for cookie in cookies:
    cookies_json[cookie['name']] = cookie['value']
pprint("浏览器cookies"+ str(cookies_json))
driver.quit()

cookies = {
    'Hm_lvt_b8f2e33447143b75e7e4463e224d6b7f': cookies_json['Hm_lvt_b8f2e33447143b75e7e4463e224d6b7f'],
    'HMACCOUNT': cookies_json['HMACCOUNT'],
    'mode': '1',
    'songIndex': '0',
    'coin_screen': '1707*1067',
    'b2d60fe00274e7c43e0c895f94b17153': '9ea2d361f75b2df0ed531eef54bf3dfc',
    'Hm_lpvt_b8f2e33447143b75e7e4463e224d6b7f': cookies_json['Hm_lpvt_b8f2e33447143b75e7e4463e224d6b7f'],
    'down_mima': 'ok',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'http://music.2t58.com',
    'Referer': 'http://music.2t58.com/down.php?ac=music&id=ZHZ2c3Zzd3hz',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

url = "http://music.2t58.com/so"
print("注意不要有空格，否则会导致程序无法正常运行！")
singer = input("请输入要爬取的歌手名或者歌名:")
print("正在爬取" + singer + "的音频----------------------------------------------------------------------------")
print("正在创建" + singer + "文件夹----------------------------------------------------------------------------")
if not os.path.exists(singer):
    os.mkdir(singer)
else:
    print("文件夹已存在")


# 1.获取总歌曲数
def get_total_data(url, singer):
    url = f"{url}/{singer}.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # 总歌曲条数
    TotalData = soup.find("div", class_="pagedata").find("span").text
    print("总歌曲数有" + TotalData + "条")
    return TotalData


# 2.计算总页数
def get_all_page(TotalData):
    # 每页只有68条数据，所以需要计算总页数
    AllPage = int(TotalData) // 68 + 1
    print("一共分页" + str(AllPage) + "页")
    return AllPage


# 3.下载歌曲并保存的函数
def download_song(params):
    song_name, song_download_key = params
    start_time = time.time()
    response = requests.get(f"http://music.2t58.com/plug/down.php?ac=music&id={song_download_key}&k=320kmp3",
                            headers=headers, cookies=cookies)
    print(f"正在下载{song_name}----------------------------------------------------------------------------")
    # 判断是否已存在文件
    if os.path.exists(f'./{singer}/{song_name}.mp3'):
        print(f"{song_name}文件已存在,覆盖下载----------------------------------------------------------------------------")

    with open(f'./{singer}/{song_name}.mp3', 'wb') as f:
        f.write(response.content)
    end_time = time.time()
    download_time = end_time - start_time
    file_size = os.path.getsize(f'./{singer}/{song_name}.mp3')
    file_size_mb = file_size / (1024 * 1024)
    print(f"{song_name}下载完成，耗时{download_time:.2f}秒，文件大小为{file_size_mb:.2f}MB----------------------------------------------------------------------------")


# 4.获取每页的歌曲列表和下载关键id,并开启多线程下载
def get_song_list(url, singer, AllPage):
    song_params = []
    for i in range(1, AllPage + 1):
        print(f"正在爬取第{i}页--------------------------------------------------------------------------------")
        res_url = f"{url}/{singer}/{i}.html"
        response = requests.get(res_url)
        soup = BeautifulSoup(response.text, "html.parser")
        song_list = soup.find_all("div", class_="play_list")
        for song in song_list:
            songs = song.find_all("li")
            for i in songs:
                really_songs = i.find_all("div", class_="name")
                song_name = ' '.join(really_songs[0].text.split()).replace(' ', '')
                song_download_key = really_songs[0].find('a')['href'].split('/')[-1][:-5]
                song_params.append((song_name, song_download_key))

    with ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(download_song, song_params)


if __name__ == "__main__":
    TotalData = get_total_data(url, singer)
    AllPage = get_all_page(TotalData)
    # 开始时间
    start_time = time.time()
    get_song_list(url, singer, AllPage)
    # 结束时间
    end_time = time.time()
    # 总耗时
    total_time = end_time - start_time
    print(f"总耗时{total_time:.2f}秒")
    print("下载完成-")