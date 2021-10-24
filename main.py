import csv
import datetime
import json
import time
import requests
from bs4 import BeautifulSoup

def get_html(url, page):
    src = requests.get(url, headers=headers).text
    with open(f'data/index_{page}.html', 'w', encoding='utf-8') as file:
        file.write(src)
    with open(f'data/index_{page}.html', encoding='utf-8') as file:
        src = file.read()
        soup = BeautifulSoup(src, 'lxml')
    return soup

def main():
    date_now = datetime.datetime.now().strftime('%Y_%m_%d__%H_%M')
    with open(f'labirint_ru_{date_now}.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            (
                'Название',
                'Автор',
                'Наличие',
                'Цена со скидкой',
                'Цена без скидки',
                'Скидка'
            )
        )
    page = 1
    url = 'https://www.labirint.ru/genres/2308/?display=table&available=1&paperbooks=1&otherbooks=1'
    books = []
    while True:
        soup = get_html(url, page)
        page_books_list = soup.find('tbody', class_='products-table__body').find_all('tr')
        for book in page_books_list:
            div_mt3 = book.find_all('div', class_='mt3')
            book_name = div_mt3[0].text.strip()
            book_author = div_mt3[1].text.strip()
            book_nalich = div_mt3[-1].text.strip()
            price = book.find('div', class_='product-pricing')
            if price.find('span', class_='price-val').find('span').text == 'Нет в продаже':
                price_new, price_old, price_sale = 0, 0, "Нет в продаже"
            else:
                price_new = int(price.find('span', class_='price-val').find('span').text.replace(' ', ''))
                try:
                    price_old = int(price.find('span', class_='price-old').text.replace(' ', ''))
                    price_sale_real = round(((price_old - price_new) / price_old) * 100)
                except Exception:
                    price_old = price_new
                    price_sale_real = 0

            books.append({
                'Название': book_name,
                'Автор': book_author,
                'Наличие': book_nalich,
                'Цена со скидкой': price_new,
                'Цена без скидки': price_old,
                'Скидка': price_sale_real
            })

            with open(f'labirint_ru_{date_now}.csv', 'a', encoding='utf-8', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(
                    (
                        book_name,
                        book_author,
                        book_nalich,
                        price_new,
                        price_old,
                        price_sale_real
                    )
                )
        page += 1

        try:
            print('[+] ' + url)
            time.sleep(2)
            next_url = soup.find('div', class_='pagination-number-viewport').find('a', class_='pagination-next__text')['href']
            url = 'https://www.labirint.ru/genres/2308/' + next_url

        except Exception:
            break

    with open(f'labirint_ru_{date_now}.json', 'w', encoding='utf-8') as file:
        json.dump(books, file, indent=4, ensure_ascii=False)

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'
}


if __name__ == '__main__':
    start = datetime.datetime.now()
    main()
    finish = datetime.datetime.now()
    print('* * * ', (finish - start), ' * * *')
