import requests as rq
from bs4 import BeautifulSoup
from selenium import webdriver
import sqlite3 as sq
from data import links_list


class ArbuzParser:

    @staticmethod
    def parse_html(**kargs):
        db = sq.connect(r'C:\Users\Alex\Desktop\Дипломная работа\Дипломный проект\foods_market_bot\tgbot\db\database.db')
        cursor = db.cursor()

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "user-agent": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }

        for link_dict in kargs['links_list']:
            product_links = []
            subcategory_ids, names, producing_countrys, brands, descriptions, costs, photos = [], [], [], [], [], [], []
            options = webdriver.ChromeOptions()
            options.set_capability('general.useragent.override',
                                   "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9")
            driver = webdriver.Chrome(
                executable_path=r'C:\Users\Alex\Desktop\Дипломная работа\Дипломаная всячина\tmp\chromedriver.exe',
                options=options
            )
            for subcategory_id in link_dict:
                product_links.clear()
                req = rq.get(url=link_dict[subcategory_id], headers=headers)
                src = req.text
                soup = BeautifulSoup(src, 'lxml')

                for product in soup.find_all('a', class_='product-card__title'):
                    product_links.append('https://arbuz.kz/' + product.get('href'))

                try:
                    for product_link in product_links:
                        driver.get(url=product_link)
                        src = driver.page_source
                        soup = BeautifulSoup(src, 'lxml')

                        subcategory_ids.append(int(subcategory_id))

                        if soup.find(class_='product-h1') is not None:
                            names.append(soup.find(class_='product-h1').text.replace('"', "'"))
                        else:
                            names.append('')

                        if soup.find('span', class_='properties--manufacturer') is not None:
                            producing_countrys.append(soup.find('span', class_='properties--manufacturer').find(class_='value').text)
                        else:
                            producing_countrys.append('')

                        if soup.find(class_='properties--brand') is not None:
                            brands.append(soup.find(class_='properties--brand').find(class_='value').text)
                        else:
                            brands.append('')

                        if soup.find('div', class_='information') is not None and '<p>' in str(soup.find('div', class_='information').find('div')):
                            descriptions.append(soup.find('div', class_='information').find('div').find('p').text.replace('"', "'"))
                        else:
                            descriptions.append('')

                        if soup.find(class_='price--wrapper price--currency_KZT') is not None:
                            costs.append(soup.find(class_='price--wrapper price--currency_KZT').text.replace('\xa0', '').replace('₸', ''))
                        else:
                            costs.append('')

                        if soup.find(class_='d-block mx-auto img-fluid') is not None:
                            photos.append(soup.find(class_='d-block mx-auto img-fluid').get('src'))
                        else:
                            photos.append('')

                except Exception as ex:
                    print(ex)
                finally:
                    driver.close()

            if len(subcategory_ids) == len(names) == len(producing_countrys) == len(brands) == len(descriptions) == len(costs) == len(photos):
                for i in range(len(subcategory_ids)):
                    cursor.execute(f'INSERT INTO products(subcategory_id, `name`, producing_country, brand, description, cost, photo)'
                                   f' VALUES ("{subcategory_ids[i]}", "{names[i]}", "{producing_countrys[i]}", "{brands[i]}", "{descriptions[i]}", "{costs[i]}", "{photos[i]}")')
                    db.commit()

            print(f'Готово! || Добавлено записей -> {len(subcategory_ids)}')

        db.close()


ArbuzParser.parse_html(links_list=links_list)
