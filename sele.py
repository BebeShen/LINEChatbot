from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException   
from bs4 import BeautifulSoup
import os
import model
from dotenv import load_dotenv
load_dotenv()
# # 背景執行
# usage:https://www.youtube.com/watch?v=Ven-pqwk3ec&t=172s
options = webdriver.ChromeOptions()
options.binary_location = os.getenv("GOOGLE_CHROME_BIN",None)
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')

browser = webdriver.Chrome(executable_path=os.getenv("CHROMEDRIVER_PATH"),chrome_options=options)
# browser = webdriver.Chrome('./chromedriver')
wait = WebDriverWait(browser, 30) # 等待載入30s
student_number = os.getenv("MY_STUDENT_NUMBER", None)
password = os.getenv("MY_NCKU_PASSWORD", None)
def login(classroom):
    # browser.get('https://app.pers.ncku.edu.tw/ncov/index.php?c=fp&bid=B102&rid=B10204901CC&floor=4F')
    url = model.get_url_by_room(classroom)
    browser.get(url)
    input = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="user_id"]')))
    input.send_keys(student_number)
    input = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="passwd"]')))
    # input.send_keys(student_password)
    input.send_keys("tttt")
    submit = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="submit_by_acpw"]')))
    submit.click() # 點選登入按鈕
    # check number/password correct
    if len(browser.find_elements_by_xpath('//*[@id="msg"]/div[2]'))>0:
        browser.close()
        print("Wrong Number/Password")
        return False
    else:
        print("Login Success")
        get_page_index()

def get_page_index():
    # browser.get('https://app.pers.ncku.edu.tw/ncov/index.php?c=fp&bid=B102&rid=B10203020&floor=3F')
    try:
        # 若為第一次登入，則會在點擊確認後前往確認身體狀況
        source = BeautifulSoup(browser.page_source,features="lxml")
        check_body = source.find_all('div',id="last_footprint_log")
        first_login = True
        if "請於關閉後填寫" not in str(check_body):
            first_login = False
        if(first_login):
            submit = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="last_footprint_log"]/div[2]/div/div[2]/div/button'))
            )
            submit.click()
            # print(browser.page_source)  # 輸出網頁原始碼
            # 確認身體狀況
            symptoms_radio = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="symptoms_N"]'))
            )
            symptoms_radio.click()
            submit_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="arch_grid"]/div[3]/form/div/div/div[3]/button[1]'))
            )
            submit_btn.click()
        else:
            submit = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="last_footprint_log"]/div[2]/div/div[2]/div/button'))
            )
            submit.click()
        browser.close()
        return "Success"
    except Exception as e:
        print(str(e))
        return "Failure on NCKU Web"
# login()