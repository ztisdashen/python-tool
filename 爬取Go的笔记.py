import os
import sys
from urllib.parse import urljoin

import requests
from lxml import etree
from lxml.html import Element

from html2md import run

CURRENT_PATH = sys.path[0]

BASE_URL = "http://www.topgoer.com/"


def check_li(li: Element) -> bool:
    """
    检查li标签是不是最内部的了
    :param li
    """
    tem_ul = li.xpath("./ul")
    if tem_ul:
        return False
    else:
        return True


def parse_li(li: Element, path: str, index: int):
    """

    :param
    """
    prefix = "000" + str(index)
    prefix = prefix[len(prefix) - 2:]
    if check_li(li):
        tem_dir = li.xpath("./a/text()")
        tem_a_url = li.xpath("./a/@href")
        if tem_dir:
            a_href = urljoin(BASE_URL, tem_a_url[0])
            #  可以得到最内部的url，进行对应的解析了
            res_ = requests.get(a_href)
            content_ = res_.text.encode("ISO-8859-1").decode('utf-8')
            file_name = path + "/{}-".format(prefix) + tem_dir[0].strip() + ".md"
            run(content_, '//*[@id="book-search-results"]/div[1]/section/*', file_name,
                base_url="http://www.topgoer.com")
            # print(file_name, a_href)
        return
    else:
        # 创建文件夹
        a_title = li.xpath("./a/text()")
        full_path = ""
        if a_title:
            # 创建文件夹
            sub_path = a_title[0].strip()
            full_path = path + "/{}-".format(prefix) + sub_path
            if not os.path.exists(full_path):
                os.makedirs(full_path)
        li_list_ = li.xpath("./ul/li")
        for i_ in range(len(li_list_)):
            parse_li(li_list_[i_], full_path, i_)


url = "http://www.topgoer.com/"
res = requests.get(url)
content = res.text.encode("ISO-8859-1").decode('utf-8')
html = etree.HTML(content)
li_list = html.xpath("//ul[@class='summary']/li")[0:17]
for i in range(len(li_list)):
    parse_li(li_list[i], CURRENT_PATH, i)
