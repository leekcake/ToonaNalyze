import os.path
import pickle
import time

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class Donation:
    def __init__(self, date, creator, nick, price, type, content):
        self.date = date
        self.creator = creator
        self.nick = nick
        self.price = price
        self.type = type
        self.content = content

    def year(self):
        return self.date[:4]

    def mouth(self):
        return self.date[5:7]

    def priceToNumber(self):
        return int( self.price.replace(",", "") )


donationList = {}


def save_cookie(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)


def load_cookie(driver, path):
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)


# return: Continue work?
def parsePage(driver: webdriver.Chrome, inx):
    print(f"{inx} 번째 도네이션 기록을 가져오고 있습니다")
    global donationList
    driver.get(f'https://toon.at/donator/mypage/donation-history/{inx}')
    driver.implicitly_wait(30)

    rows = driver.find_elements(By.TAG_NAME, 'tr')
    del rows[0]
    added = 0
    for row in rows:
        datas = row.find_elements(By.TAG_NAME, 'td')
        key = datas[0].text

        if datas[0].text in donationList:
            print(f"Detected Duplicate: {datas[0].text} on {inx}")
            continue

        donationList[datas[0].text] = Donation(datas[0].text, datas[1].text, datas[2].text, datas[3].text, datas[4].text, datas[5].text)
        added += 1

    return added

def parseQuest(driver: webdriver.Chrome, inx):
    print(f"{inx} 번째 퀘스트 기록을 가져오고 있습니다")
    global donationList
    driver.get(f'https://toon.at/donator/mypage/quest-donation-history/{inx}')
    driver.implicitly_wait(30)

    rows = driver.find_elements(By.TAG_NAME, 'tr')
    del rows[0]
    for row in rows:
        datas = row.find_elements(By.TAG_NAME, 'td')
        if datas[4].text == "진행중" or datas[4].text == "등록 취소" or datas[4].text == "거절됨":
            continue
        if datas[0].text in donationList:
            return False
        donationList[datas[0].text] = Donation(datas[0].text, datas[1].text, datas[2].text, datas[3].text,
                                          f"퀘스트({datas[4].text})", datas[6].text)

    return len(rows) != 0


def main():
    global donationList
    if os.path.exists('donationList.pickle'):
       print("이미 도네이션 기록이 있습니다? 캐시본이 사용됩니다.")

       print("파일에서 도네이션 기록을 가져오고 있습니다...")
       with open('donationList.pickle', 'rb') as fb:
           donationList = pickle.load(fb)
       print(" 완료!")

    # Read from Chrome
    if True:
        dc = DesiredCapabilities.CHROME
        dc['goog:loggingPrefs'] = {'browser': 'ALL'}
        chrome_options = Options()
        driver = webdriver.Chrome(desired_capabilities=dc, options=chrome_options)
        driver.get(f'https://toon.at/')
        driver.implicitly_wait(30)
        if os.path.exists('login.pickle'):
            load_cookie(driver, 'login.pickle')

        driver.get(f'https://toon.at/donator/mypage/donation-history')
        driver.implicitly_wait(30)
        endCount = 0
        print("도네이션 기록을 기다리는중")
        while driver.current_url != "https://toon.at/donator/mypage/donation-history":
            time.sleep(1)
            driver.implicitly_wait(30)

        save_cookie(driver, 'login.pickle')

        inx = 1
        while parsePage(driver, inx):
            inx += 1

        inx = 1

        while parseQuest(driver, inx):
            inx += 1

        print(" 완료!")

        with open('donationList.pickle', 'wb') as fb:
            pickle.dump(donationList, fb)

        print("도네이션 기록을 가져왔습니다.")

    donate: Donation

    totalSet = {}

    building = []
    for donate in donationList.values():
        building.append(f"<tr><td>{donate.date}</td>"
                        f"<td>{donate.creator}</td>"
                        f"<td>{donate.nick}</td>"
                        f"<td>{donate.price}</td>"
                        f"<td>{donate.type}</td>"
                        f"<td>{donate.content}</td></tr>")

    with open('base.htm', 'r', encoding='utf8') as f:
        html = f.read()

    html = html.replace("//DATA//", ''.join(building))

    with open('donateList.htm', 'w', encoding='utf8') as f:
        f.write(html)

    for donate in donationList.values():
        if donate.creator not in totalSet:
            totalSet[donate.creator] = {}
        if donate.year() not in totalSet[donate.creator]:
            totalSet[donate.creator][donate.year()] = {}
        if donate.mouth() not in totalSet[donate.creator][donate.year()]:
            totalSet[donate.creator][donate.year()][donate.mouth()] = 0

        totalSet[donate.creator][donate.year()][donate.mouth()] += donate.priceToNumber()

    for name, years in totalSet.items():
        print(f"==={name}===")
        nameTotal = 0
        for year, mouths in years.items():
            print(f"==={year}===")
            total = 0
            for mouth, result in mouths.items():
                total += result
                nameTotal += result
                print(f"{year}-{mouth}: {result}")
            print(f"{year}: {total}")
        print(f"==={name}===: {nameTotal}")



if __name__ == '__main__':
    main()
