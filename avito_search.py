from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
import csv
import time
from selenium.webdriver.common.keys import Keys

# Входные данные
city = 'новосибирск'
category = 'Коллекционирование'
word = 'lego'
price = 5000
# Имя файла для репорта
reportFileName = 'test.csv'

# Решил вести лог, через print
browser = webdriver.Chrome('E:/fs/chromedriver.exe')
browser.get('https://avito.ru/krasnoyarsk')

print('BEGIN ### Choose City ###')
print(f'\tТекущий url: {browser.current_url}')

# Жмем на смену города
browser.find_element_by_xpath('//div[@data-marker="search-form/location"]').click()

try:
    WebDriverWait(browser, 10)
    # Находим поле для ввода
    pole = browser.find_element_by_xpath('//input[@data-marker="popup-location/region/input"]')
    # Вводим город
    pole.send_keys(city)
finally:
    print('\tВвели город')

# Костыль
try:
    pole.send_keys(Keys.ENTER)
finally:
    print('\tУбрали фокус с инпута')

# Спим
time.sleep(3)
try:
    pole.send_keys(Keys.ENTER)
    # Жмем кнопку отправки формы
    browser.find_element_by_xpath('//button[@data-marker="popup-location/save-button"]').click()
finally:
    print('\tСабмитнули')

print(f'\tТекущий url: {browser.current_url}')
print('END ### Choose City ###')


def fillFilters():
    print('BEGIN ### fillFilters ###')

    agreeXPath = '//button[@data-marker="location/tooltip-agree"]'
    categoryXPath = f'//select[@name="category_id"]/option[text()="{category}"]'
    nameXPath = '//input[@id="search" and @data-marker="search-form/suggest"]'
    priceXPath = '//input[@data-marker="price/from"]'
    submitXPath = '//button[@data-marker="search-filters/submit-button"]'

    try:
        WebDriverWait(browser, 10)
        # Выбираем категорию
        browser.find_element_by_xpath(categoryXPath).click()
        print('\tКатегория выбрана')

        browser.get(browser.current_url)

        try:
            WebDriverWait(browser, 10)
            # Вводим поисковое слово
            browser.find_element_by_xpath(nameXPath).send_keys(word)
            print('\tСлово введено')
            '''
            browser.find_element_by_xpath('//div[@data-marker="search-form/geofilters"]').click()
            
            try:
                WebDriverWait(browser, 10)
                # Еще костыль (facepalm)
                time.sleep(3)
                browser.find_element_by_xpath('//label/span[text()="25"]').click()
                browser.find_element_by_xpath('//button[@data-marker="popup-location/save-button"]').click()
            finally:
                print('\tВыбрали радиус')
            '''
            try:
                WebDriverWait(browser, 10)
                # Вводим цену ОТ 5000
                browser.find_element_by_xpath(priceXPath).send_keys(price)
            finally:
                print('\tЦена введена')
        finally:
            print()


        # Применяем фильтр
        browser.find_element_by_xpath(submitXPath).click()
    finally:
        print('\tФильтры заполнены и применены\n')

    print('END ### fillFilters ###')

def getItemURLs():
    print('BEGIN ### getItemURLs ###')
    itemCountXPath = '//span[@class="page-title-count"]'
    linkXPath = '//a[@itemprop="url"]'

    browser.get(browser.current_url)

    try:
        WebDriverWait(browser, 10)
        # Получаем кол-во найденных результатов
        itemCount = browser.find_element_by_xpath(itemCountXPath).text
        itemCount = int(itemCount)

        iz = browser.find_elements_by_xpath('//div[@data-marker="item"]')
        print(len(iz))

        itemCount = len(iz)
        #browser.close()

        print(f'\tНайдено: {itemCount}')

        # Достаем адреса айтемов #
        itemURLs = []
        for i in range(itemCount):
            # ищем линки с аттрибутом
            items = browser.find_elements_by_xpath(linkXPath)

            # Финт ушами. Ищем вхождение города в тайтле ссылки
            nsk = f'в {city}е'
            st = items[i].get_attribute('title')
            st = str(st)
            # Если найдено совпадение,
            if (st.find(nsk)):
                # ..то добавляем линк в массив
                itemURLs.append(items[i].get_attribute('href'))
            else:
                # Иначе, прерываем итерации, считаем что пошли уже айтемы с доставкой из другого города
                break

    finally:
        # Смотрим что лежит в массиве #
        # for i in range(len(itemURLs)):
        #    print(itemURLs[i])

        print('\tЗаписали адреса айтемов в массив\n')

    print('END ### getItemURLs ###')
    return itemURLs

def getItemsInfo(itemURLs):
    print('BEGIN ### getItemsInfo ###')

    iHeadXPath = '//span[@class="title-info-title-text"]'
    iAddressXPath = '//span[@class="item-address__string"]'
    iPriceXPath = '//*[@id="price-value"]/span/span[1]'

    resultArray = []
    for i in range(len(itemURLs)):
        # переходим к айтему
        browser.get(itemURLs[i])

        # Устанавливаем текущий юрл
        browser.get(browser.current_url)

        # Собираем словарь
        resultDict = {}
        try:
            WebDriverWait(browser, 10)
            # Получаем инфо
            iHead = browser.find_element_by_xpath(iHeadXPath).text
            iAddress = browser.find_element_by_xpath(iAddressXPath).text
            iPrice = browser.find_element_by_xpath(iPriceXPath).get_attribute('content')
            iURL = itemURLs[i]
        finally:
            print(f'\tДанные получены для: {itemURLs[i]}')

        # Записываем данные айтема в словарь
        resultDict = {'Название': iHead, 'Адрес': iAddress, 'Цена': iPrice, 'Ссылка': iURL}
        # Добавляем запись в общий массив
        resultArray.append(resultDict)
        print('\t..и записаны в словарь')
    # Возвращаем массив, содержащий словари
    print('\tВсе данные записаны в словарь\n')
    print('END ### getItemsInfo ###')
    return resultArray

def writeToFile(result):
    print('BEGIN ### writeToFile ###')

    # Создаем файл для записи
    try:
        with open(reportFileName, "w", newline="") as file:
            # Определяемзаголовки
            columns = ["Название", "Адрес", "Цена", "Ссылка"]
            writer = csv.DictWriter(file, delimiter=';', fieldnames=columns)
            writer.writeheader()
            # Пишем данные в файл
            writer.writerows(result)
    finally:
        print(f'\tДанные записаны в {reportFileName}')

    print('END ### writeToFile ###')


''' ДЕЛАЕМ МАГИЮ %) '''
fillFilters()
itemURLs = getItemURLs()
resultArray = getItemsInfo(itemURLs)
writeToFile(resultArray)
