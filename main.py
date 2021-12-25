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

    def priceToNumber(self):
        return int( self.price.replace(",", "") )

donationList = []


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
    for row in rows:
        datas = row.find_elements(By.TAG_NAME, 'td')
        donationList.append(Donation(datas[0].text, datas[1].text, datas[2].text, datas[3].text, datas[4].text, datas[5].text))

    return len(rows) != 0


def main():
    global donationList
    if os.path.exists('donationList.pickle'):
       print("이미 도네이션 기록이 있습니다? 캐시본이 사용됩니다.")

    if not os.path.exists('donationList.pickle'):
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

        print(" 완료!")

        inx = 1
        while parsePage(driver, inx):
            inx += 1

        with open('donationList.pickle', 'wb') as fb:
            pickle.dump(donationList, fb)
    else:
        print("파일에서 도네이션 기록을 가져오고 있습니다...")
        with open('donationList.pickle', 'rb') as fb:
            donationList = pickle.load(fb)

    print("도네이션 기록을 가져왔습니다.")
    donate: Donation

    totalSet = {}

    for donate in donationList:
        if donate.creator not in totalSet:
            totalSet[donate.creator] = {}
        if donate.year() not in totalSet[donate.creator]:
            totalSet[donate.creator][donate.year()] = 0

        totalSet[donate.creator][donate.year()] += donate.priceToNumber()

    for name, years in totalSet.items():
        print(f"==={name}===")
        for year, result in years.items():
            print(f"{year}: {result}")



if __name__ == '__main__':
    main()
