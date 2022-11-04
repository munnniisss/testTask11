from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def init_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver


def auth(driver, login, password):
    driver.get('https://wordstat.yandex.by/')

    # Ожидание загрузки страницы
    loading_elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'l-content__text')))
    driver.find_element(By.XPATH, '/html/body/div[1]/table/tbody/tr/td[6]/table/tbody/tr[1]/td[2]/a/span').click()
    loading_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'b-domik__title')))
    driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td[2]/div/div[2]/span/span/input').send_keys(login)
    driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td[2]/div/div[3]/span/span/input').send_keys(
        password)
    driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td[2]/div/div[5]/span[1]/input').click()

    return driver


def parse_by_words(driver, keyword):
    result_full = []
    result_same = []

    pages = 1
    status = True

    while status:
        full = []
        same = []

        # отвечает за то, какую сейчас таблицу на странице парсим (0 - левая, 1 - правая)
        count = 0

        driver.get(f'https://wordstat.yandex.by/#!/?page={pages}&words={keyword}')
        try:
            loading_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'b-word-statistics__table')))
        except TimeoutException:
            status = False

        html_data = driver.page_source

        soup = BeautifulSoup(html_data, 'lxml')
        tables = soup.findAll('table', class_='b-word-statistics__table')

        for table in tables:
            phrases = table.findAllNext('tr', class_='b-word-statistics__tr')
            for phrase in phrases:
                if count:
                    try:
                        same.append(
                            (phrase.findNext('td', class_='b-word-statistics__td b-word-statistics__td-phrase').text.
                             replace('\xa0', ''),
                             phrase.findNext('td', class_='b-word-statistics__td b-word-statistics__td-number').text.
                             replace('\xa0', '')))
                    except AttributeError:
                        break
                else:
                    try:
                        full.append(
                            (phrase.findNext('td', class_='b-word-statistics__td b-word-statistics__td-phrase').text.
                             replace('\xa0', ''),
                             phrase.findNext('td', class_='b-word-statistics__td b-word-statistics__td-number').text.
                             replace('\xa0', '')))
                    except AttributeError:
                        break
            count += 1

        try:
            full.pop(0)
            same.pop(0)
        except IndexError:
            status = False
        finally:
            result_same += same
            result_full += full

        pages += 1

        time.sleep(5)

    return [result_full, result_same]


def parse_by_regions(driver):
    result_regions = []
    status = True
    while status:
        driver.get(f'https://wordstat.yandex.by/#!/regions?words={keyword}')

        try:
            loading_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,
                                                                                           'b-regions-statistic__table')))
        except TimeoutException:
            status = False

        html_data = driver.page_source

        soup = BeautifulSoup(html_data, 'lxml')

        regions = soup.findAll('tr', class_=['b-regions-statistic__tr',
                                             'b-regions-statistic__tr b-regions-statistic__tr_type_even'])

        for region in regions:
            info = region.findAllNext('td')
            data_tup = (info[0].text, info[1].text.replace('\xa0', ''), info[2].text.replace('\xa0', ''))
            result_regions.append(data_tup)

        status = False
    return result_regions


def main(keyword, login, password):
    driver = auth(init_driver(), login, password)
    full, same = parse_by_words(driver, keyword)
    regions = parse_by_regions(driver)

    return [full, same, regions]


if __name__ == '__main__':
    login = 'munnniisss'
    password = 'az8794az'
    keyword = 'зов мебели'

    print(main(keyword, login, password))
