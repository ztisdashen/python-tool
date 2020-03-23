from io import TextIOWrapper

from lxml import etree
import re
from bs4 import BeautifulSoup

# code_classes = ["language-bash","language-yaml"]
from lxml.html import Element
from typing.io import TextIO


def del_with_ul(tag: Element, file: TextIO, space_num=0, prefix=None):
    """
    :param file: 文件
    :param prefix: 前缀
    :arg tag 包含ul的标签
    :arg space_num 空格个数控制格式
    tag的格式是
    """
    tag = etree.HTML(etree.tostring(tag, encoding="utf-8", pretty_print=True, method="html").decode())
    li = tag.xpath("/html/body/ul/li")
    # 没有li标签
    if not li:
        return
    elif len(li) == 0:
        return
    else:
        for k in li:
            if not prefix:
                line = " " * space_num + "* " + k.xpath("./text()")[0].replace("\n", "") + "\n"
                file.write(line)
                # print(" " * space_num, "*", k.xpath("./text()")[0].replace("\n", ""))
            else:
                line = prefix + " " + " " * space_num + "* " + k.xpath("./text()")[0].replace("\n", "") + "\n"
                file.write(line)
                # print(prefix, end="")
                # print(" " * space_num, "*", k.xpath("./text()")[0].replace("\n", ""))
            tem = k.xpath("./ul")
            if tem is not None and len(tem) > 0:
                del_with_ul(tem[0], space_num=space_num + 1, file=file)


def del_with_blockquote(tag: Element, file: TextIO):
    """
    :param file:
    :arg tag 含有blockquote的标签
    """

    children = tag.xpath("/html/body/blockquote/*")
    for i in children:
        sub = etree.tostring(i, encoding="utf-8", pretty_print=True, method="html").decode()
        sub_html = etree.HTML(sub)
        tag_p = sub_html.xpath("/html/body/p")
        if tag_p:
            # line_to_print = "".join(tag_p[0].xpath(".//text()")).replace("\n", "")
            line = ">" + "".join(tag_p[0].xpath(".//text()")).replace("\n", "") + "\n"
            file.write(line)
            # print(">", "".join(tag_p[0].xpath(".//text()")).replace("\n", ""))
        else:
            del_with_ul(sub_html, prefix=">", file=file)


def del_with_h(line: str, level: int, file: TextIO):
    """
    :arg
    """
    line = "#" * level + " " + line + "\n"
    file.write(line)


def del_with_p(data, file: TextIO):
    line = "".join(data[0].xpath(".//text()")).replace("\n", "") + "\n"
    file.write(line)


def del_with_table(sub: Element, file: TextIO):
    col_num = 0
    col_name = sub.xpath("//thead/tr/th/text()")
    col_num = len(col_name)
    row_head = "| " + " | ".join(col_name) + " |\n"
    file.write(row_head)
    # print(row_head)
    tem_list = "| " + " | ".join([":-----:" for i in range(col_num)]) + " |\n"
    # print(tem_list)
    file.write(tem_list)
    # 解决表体
    trs = sub.xpath("//tbody/tr")
    for tr in trs:
        row = tr.xpath("./td/text()")
        row_each = "| " + " | ".join(row).replace("\n", "") + " |\n"
        file.write(row_each)


def pre_processing(data: str):
    # 处理短的代码块
    if data.find("<code>"):
        data = data.replace("<code>", "`").replace("</code>", '`')
    # 处理粗体
    if data.find("<strong>"):
        data = data.replace("<strong>", "**").replace("</strong>", "**")
    #  处理img
    if data.find("<img"):
        img_urls = re.findall(img_, data)
        for img_url in img_urls:
            data = re.sub("<img.*?>", "![]({})".format(img_url), data, count=1, flags=re.S)
    return data


def del_with_code_block(code_type: str, code: str, file: TextIO):
    other = ["vue", "xml", "html","java"]
    code_ = code
    if code_type in other:
        code_ = code.replace("&lt;", "<").replace("&gt;", ">")
    line = "```" + code_type + "\n" + code_ + "\n```\n"
    file.write(line)


h2 = re.compile("<h2>(.*?)</h2>", re.S)
h3 = re.compile("<h3>(.*?)</h3>", re.S)
h4 = re.compile("<h4>(.*?)</h4>", re.S)
pre = re.compile('<pre><code class="language-(.*?)">(.*?)</code></pre>', re.S)
ul = re.compile("<ul>(.*?)</ul>", re.S)
code = re.compile(".*?<code>(.*?)</code>.*?", re.S)
# 普通的<p>标签
p = re.compile("^<p>(.*?)</p>", re.S)
blockquote = re.compile("<blockquote>(.*?)</blockquote>", re.S)
table = re.compile("<table>(.*?)</table>", re.S)
img_ = re.compile("<img.*?src=[\'\"](.*?)[\'\"].*?>", flags=re.S)
# 处理a标签
a = re.compile("<a.*?href=[\'\"](.*?)[\'\"]>(.*?)</a>", re.S)


def run(html_str: str, xpath: str, file_name: str):
    """
    :param html_str 网页html代码
    :param xpath xpath
    :param file_name 输出文件名
    """
    with open(file=file_name, mode="w", encoding="utf-8") as text_file:
        text_file.write("# " + file_name.split(".")[0] + "\n")
        html = etree.HTML(html_str)
        # 处理 a 标签
        texts = html.xpath("//a/text()")
        hrefs = html.xpath("//a/@href")
        for i in range(len(texts)):
            texts[i] = texts[i].replace("\n", "").replace(" ", "")
        for index in range(len(texts)):
            html_str = re.sub("<a.*?/a>", "[{}]({})".format(texts[index], hrefs[index]), html_str, count=1, flags=re.S)
        html = etree.HTML(html_str)
        ress = html.xpath(xpath)
        for i in ress:
            s = etree.tostring(i, encoding="utf-8", pretty_print=True, method="html").decode()
            r4 = re.match(pre, s)
            # 其中的代码部分
            if r4:
                del_with_code_block(r4.groups()[0], r4.groups()[1], text_file)
                continue
            s = pre_processing(s)
            r1 = re.match(h2, s)
            if r1:
                del_with_h(r1.groups()[0], level=2, file=text_file)
                continue
            r2 = re.match(h3, s)
            if r2:
                del_with_h(r2.groups()[0], level=3, file=text_file)
                continue
            r3 = re.match(h4, s)
            if r2:
                del_with_h(r3.groups()[0], level=4, file=text_file)
                continue
            r5 = re.match(ul, s)
            if r5:
                sub = etree.HTML(s)
                del_with_ul(sub, text_file)
                continue
            r7 = re.match(blockquote, s)
            if r7:
                sub = etree.HTML(s)
                del_with_blockquote(sub, text_file)
                continue
            r8 = re.match(table, s)
            if r8:
                sub = etree.HTML(s)
                del_with_table(sub=sub, file=text_file)
                continue
            h = etree.HTML(s)
            tem = h.xpath("/html/body/p")
            if tem:
                del_with_p(tem, file=text_file)
    print(file_name, "完成")


if __name__ == '__main__':
    with open("dddd.html", mode="r", encoding="utf8") as f:
        run(f.read(), "//div[@class='content-item-summary']/div[1]/*", "test.md")
