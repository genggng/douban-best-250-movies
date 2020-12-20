# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import xlwt
import time
import random


# 爬取页面内容
def request_douban(url):
    headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 \
    Safari/537.36'}
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        return None


book = xlwt.Workbook(encoding='utf-8', style_compression=0)

#新建页
sheet = book.add_sheet('douban_best250_movies', cell_overwrite_ok=True)
sheet.write(0, 0, '名称')
sheet.write(0, 1, '链接')
sheet.write(0, 2, '导演')
sheet.write(0, 3, '演员')
sheet.write(0, 4, '类型')

total_num = 1



# 爬取并保存子页面
def save_subPage(sub_url):
    sub_html = request_douban(sub_url)
    sub_soup = BeautifulSoup(sub_html,"lxml")

    name = sub_soup.find('div',attrs={'id':'content'}).find('h1').find('span',attrs={'property':'v:itemreviewed'}).string

    info = sub_soup.find('div',attrs={'id':'info'})
    director = info.find('a',attrs={'rel':'v:directedBy'}).string

    actor_list = info.find_all('a',attrs={'rel':'v:starring'})
    actors = '/'.join([t.string for t in actor_list])

    type_list = info.find_all('span',attrs={'property':'v:genre'})
    types = '/'.join([t.string for t in type_list])

    global total_num

    sheet.write(total_num, 0, name)
    sheet.write(total_num, 1, sub_url)
    sheet.write(total_num, 2, director)
    sheet.write(total_num, 3, actors)
    sheet.write(total_num, 4, types)

    total_num += 1
    print('爬取电影：' + str(total_num) +'  ' + name + ' | ' + director + ' | ' + types )

# 广度优先从主页面获取子页面url
def index(page):
    url = 'https://movie.douban.com/top250?start=' + str(page * 25) + '&filter='
    html = request_douban(url)
    soup = BeautifulSoup(html, 'lxml')
    list = soup.find(class_="grid_view").find_all('li')
    for item in list:
        sub_url = item.find('a').get('href')
        time.sleep(random.random()*3)   #应对反爬虫机制
        save_subPage(sub_url)



if __name__ == '__main__':

    for i in range(0, 10):
        index(i)

book.save('douban_best250_movies.xls')