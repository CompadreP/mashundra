import pandas as pd
import requests
from bs4 import BeautifulSoup

########################################################################################################################
#                                        ЭТО СТАРЫЙ КОД
########################################################################################################################

# icd = open('data/ICD10.csv', 'rb')
# icdvoc = pd.read_csv(icd)
# il = icdvoc['concept_code'].unique().tolist()
# # #driver = webdriver.Chrome("chromedriver.exe")
#
# k = []

# for j in il:
#     # driver.request.get("https://icdlist.com/icd-10/"+j)
#     s = requests.Session()
#     page = s.get("https://icdlist.com/icd-10/"+j)
#     # content = request.page_source
#     soup = BeautifulSoup(page.content, 'html.parser')
#     a = soup.find_all('section', id='Synonyms-' + j.replace('.', ''))
#     for r in a:
#         k.append([r.find('ul'), j])
#     print(k)
# request.close()


########################################################################################################################
#                                        ЭТО НОВЫЙ КОД
########################################################################################################################

import csv
import datetime
import os
from concurrent.futures import ProcessPoolExecutor

from selenium import webdriver


# чтобы такие штуки не хардкодить, есть методы, но это тема отдельной лекции
# (если кратко - используются переменные среды)
PROCESSES_COUNT = 5
CHROME_DRIVER_PATH = "/Users/emoiseev/chromedriver"


# для параллелизации очень важно выделить то, что будет делаться в отдельном процессе,
# и что не будет изменять какие-то глобальные переменные (поэтому тут на вход подается
# идентификатор, а не используется общий список, иначе параллелизма не достичь
def process_one_decease_id(decease_id):
    driver = webdriver.Chrome(CHROME_DRIVER_PATH)
    driver.get(f"https://icdlist.com/icd-10/{decease_id}")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    parent_ul_element = soup.find('section',
                                  id=f"Synonyms-{decease_id.replace('.', '')}")
    synonyms = []
    if parent_ul_element:
        ul_element = parent_ul_element.find('ul')
        for li_element in ul_element.contents:
            synonyms.append(li_element.text)
    return synonyms


def main():
    il = set()

    with open(os.path.join('data', 'ICD10.csv')) as csvfile:
        icd = csv.reader(csvfile)

        for n, row in enumerate(icd):
            if n == 0:
                continue
            concept_code = row[0]
            il.add(concept_code)

    il = list(il)[:100]
    synonyms_dict = {}

    # тут собственно создается пул процессов, который будет исполнять задачи параллельно
    with ProcessPoolExecutor(PROCESSES_COUNT) as executor:
        for decease_id, synonyms in zip(il, executor.map(process_one_decease_id, il)):
            synonyms_dict[decease_id] = synonyms

    for k, v in synonyms_dict.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    print(f"Start - {datetime.datetime.now().isoformat()}")
    main()
    print(f"End - {datetime.datetime.now().isoformat()}")
