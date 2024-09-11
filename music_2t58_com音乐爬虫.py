import time

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import os

cookies = {
    'Hm_lvt_b8f2e33447143b75e7e4463e224d6b7f': '1726051102',
    'HMACCOUNT': 'AD6D3F7F0821F20E',
    'mode': '1',
    'songIndex': '0',
    'coin_screen': '1707*1067',
    'b2d60fe00274e7c43e0c895f94b17153': '9ea2d361f75b2df0ed531eef54bf3dfc',
    'Hm_lpvt_b8f2e33447143b75e7e4463e224d6b7f': '1726057805',
    'down_mima': 'ok',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'Cookie': 'Hm_lvt_b8f2e33447143b75e7e4463e224d6b7f=1726051102; HMACCOUNT=AD6D3F7F0821F20E; mode=1; songIndex=0; coin_screen=1707*1067; b2d60fe00274e7c43e0c895f94b17153=9ea2d361f75b2df0ed531eef54bf3dfc; Hm_lpvt_b8f2e33447143b75e7e4463e224d6b7f=1726057805; down_mima=ok',
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
def download_song(song_name, song_download_key):
    start_time = time.time()
    response = requests.get(f"http://music.2t58.com/plug/down.php?ac=music&id={song_download_key}&k=320kmp3",
                            headers=headers, cookies=cookies)
    print(f"正在下载{song_name}----------------------------------------------------------------------------")
    # 判断是否已存在文件
    if os.path.exists(f'./{singer}/{song_name}.mp3'):
        print(
            f"{song_name}文件已存在,覆盖下载----------------------------------------------------------------------------")

    with open(f'./{singer}/{song_name}.mp3', 'wb') as f:
        f.write(response.content)
    end_time = time.time()
    download_time = end_time - start_time
    file_size = os.path.getsize(f'./{singer}/{song_name}.mp3')
    file_size_mb = file_size / (1024 * 1024)
    print(
        f"{song_name}下载完成，耗时{download_time:.2f}秒，文件大小为{file_size_mb:.2f}MB----------------------------------------------------------------------------")


# 4.获取每页的歌曲列表和下载关键id,并开启多线程下载
def get_song_list(url, singer, AllPage):
    count = 0
    for i in range(1, AllPage + 1):
        print(f"正在爬取第{i}页--------------------------------------------------------------------------------")
        res_url = f"{url}/{singer}/{i}.html"
        response = requests.get(res_url)
        soup = BeautifulSoup(response.text, "html.parser")
        song_list = soup.find_all("div", class_="play_list")
        # 遍历song_list里面的所有ul下面的li
        for song in song_list:
            songs = song.find_all("li")
            # count = 0  计数器放这就是每页重置
            for i in songs:
                count = count + 1
                really_songs = i.find_all("div", class_="name")
                song_name = ' '.join(really_songs[0].text.split()).replace(' ', '')
                song_download_key = really_songs[0].find('a')['href'].split('/')[-1][:-5]
                print(f"第{count}首" + '  ' + song_name + '  ' + "下载地址关键值为" + song_download_key)
                # 使用线程池下载歌曲
                with ThreadPoolExecutor(max_workers=10) as executor:
                    executor.submit(download_song, song_name, song_download_key)



