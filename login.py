import json
from time import time
from urllib.parse import urlencode
import requests

username = ""
pwd = ""
with open("account.txt", mode="r") as f:
    username = f.readline().replace("\n", "")
    pwd = f.readline().replace("\n", "")


def run(username: str, password: str):
    session = requests.Session()
    data = {
        "username": username,
        "grant_type": "password",
        "password": password,
        "imageCodeResult": "",
        "imageKey": ""
    }
    token_url = "http://stuinfo.neu.edu.cn/api/auth/oauth/token?{}".format(urlencode(data))
    # print(token_url)
    headers = {
        "Authorization": "Basic dnVlOnZ1ZQ==",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "http://stuinfo.neu.edu.cn/",
    }
    payload = {"_t": str(int(time()))}
    res = session.post(token_url, headers=headers)
    access_token = json.loads(res.text)
    headers["Authorization"] = "Bearer " + access_token["access_token"]
    session.cookies["userName"] = username
    session.cookies["accessToken"] = access_token["access_token"]
    cookie = "accessToken={}; userName={}".format(access_token["access_token"], username)
    headers["Cookie"] = cookie
    login_url = "http://stuinfo.neu.edu.cn/cloud-xxbl/studenLogin"
    res = session.post(login_url, headers=headers)
    tag = json.loads(res.text)
    info_url = "http://stuinfo.neu.edu.cn/cloud-xxbl/studentinfo?tag={}".format(tag["data"])
    info_res = session.get(info_url, headers=headers)
    # print(info_res.text)
    # print(dict(info_res.cookies))
    JSESSIONID = dict(info_res.cookies)["JSESSIONID"]
    get_info_url = 'http://stuinfo.neu.edu.cn/cloud-xxbl/getStudentInfo'
    # headers["Referer"] = info_url
    cookie = cookie + "; {}".format("JSESSIONID=" + JSESSIONID)
    session.cookies["JSESSIONID"] = JSESSIONID
    headers["Cookie"] = cookie
    get_info_res = session.get(get_info_url, headers=headers)
    get_info_data = json.loads(get_info_res.text)
    # print(headers["Cookie"])
    get_info_data["data"].pop("xgrq")
    get_info_data["data"].pop("ipcity")
    get_info_data["data"].pop("ipstr")
    get_info_data["data"].pop("tbsj")
    tem_ = get_info_data["data"]
    # print(tem_)
    form_data = '''zjtw: ""
    zzkssj: ""
    sfjy: ""
    sfyqjc: ""
    mqsfzj: ""
    jtms: ""
    glyyms: ""
    gldxxdz_sf: ""
    gldxxdz: ""
    mqstzk: ""
    sfgcyiqz: "否"
    cjlqk: "曾经医学观察，后隔离解除"
    dsjtqkms: ""
    hjnznl: "家"
    qgnl: "家"
    sfqtdqlxs: "否"
    sfqtdqlxsmsxj: ""
    sfjcgbr: "否"
    sfjcgbrmsxj: ""
    sfjcglxsry: "否"
    sfjcglxsrymsxj: ""
    sfjcgysqzbr: "否"
    sfjcgysqzbrmsxj: ""
    sfjtcyjjfbqk: "否"
    sfjtcyjjfbqkmsxj: ""
    sfqgfrmz: "否"
    yljgmc: ""
    zzzd: ""
    sfygfr: "无"
    zgtw: ""
    zgtwcxsj: ""
    sfyghxdbsy: "无"
    sfyghxdbsycxsj: ""
    sfygxhdbsy: "无"
    sfygxhdbsycxsj: ""
    sfbrtb: "是"
    fdysfty: "否"
    tbrxm: ""
    tbrxh: ""
    tbrxy: ""
    dtyy: ""'''
    form_data_ = {i.split(":")[0]: i.split(":")[1].replace('"', "").replace(" ", "") for i in form_data.split("\n")}
    for k, v in tem_.items():
        if k not in form_data_.keys():
            form_data_[k] = v
    # print(form_data_)
    submit_url = "http://stuinfo.neu.edu.cn/cloud-xxbl/updateStudentInfo?t=" + str(int(time() * 1000))
    res_submit = session.post(url=submit_url, data=json.dumps(form_data_), headers=headers)
    return json.loads(res_submit.text)


if __name__ == '__main__':
    run(username=username, password=pwd)
