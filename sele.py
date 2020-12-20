from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
load_dotenv()
# # 背景執行
# options = webdriver.ChromeOptions()
# options.add_argument('--headless')

# browser = webdriver.Chrome(chrome_options=options, executable_path='./chromedriver')
browser = webdriver.Chrome('./chromedriver')
# browser.maximize_window()  # 最大化視窗
wait = WebDriverWait(browser, 30) # 等待載入30s
student_number = os.getenv("MY_STUDENT_NUMBER", None)
password = os.getenv("MY_NCKU_PASSWORD", None)
def login():
    browser.get('https://app.pers.ncku.edu.tw/ncov/index.php?c=fp&bid=B029&rid=B02902006&floor=2F')
    input = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="user_id"]')))
    input.send_keys(student_number)
    input = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="passwd"]')))
    input.send_keys(password)
    submit = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="submit_by_acpw"]')))
    submit.click() # 點選登入按鈕
    get_page_index()

def get_page_index():
    # browser.get('https://app.pers.ncku.edu.tw/ncov/index.php?c=fp&bid=B102&rid=B10203020&floor=3F')
    try:
        # 若為第一次登入，則會在點擊確認後前往確認身體狀況
        source = BeautifulSoup(browser.page_source)
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
    except Exception as e:
        print(str(e))
login()