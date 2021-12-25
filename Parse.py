# coding: utf-8

# In[1]:


import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import telebot
import schedule
import time
import random
from fake_useragent import UserAgent
import os

pass_to_project = ""

# In[2]:

token = str(os.environ['token'])

bot = telebot.TeleBot(token)


def prepare_txt_files(new_filename, old_filename):
    open(old_filename, 'w').close()

    new = open(new_filename, 'r')
    old = open(old_filename, 'w')
    old.write(new.read())
    new.close()
    old.close()

    open(new_filename, 'w').close()


def add_sneakers_scrap(filename, sneakers_names, sneakers_links,
                       sneakers_photo,
                       sneakers_prices_old, sneakers_prices, sneakers_types,
                       sneakers_sizes):
    site_scrap = open(filename, 'a')

    for i in range(len(sneakers_names)):
        site_scrap.write(sneakers_names[i] + '\n')
        site_scrap.write(sneakers_links[i] + '\n')
        site_scrap.write(sneakers_photo[i] + '\n')
        site_scrap.write(sneakers_prices_old[i] + '\n')
        site_scrap.write(sneakers_prices[i] + '\n')
        site_scrap.write(sneakers_types[i] + '\n')
        site_scrap.write(', '.join(sneakers_sizes[i]) + '\n')
        site_scrap.write('\n')

    site_scrap.close()


# In[3]:


def get_response(link):
    cookie = 'PHPSESSID=be1cbcdcb8a79ee11d5277f1758532c1; currency=RUB; rerf=AAAAAGDPGg2VCqVoA87yAg==; ipp_uid=1624185357165/6CuaoVC8L6R3lgbU/Gt+OBJDHbIPZLzuOxsddXQ==; ipp_uid1=1624185357165; ipp_uid2=6CuaoVC8L6R3lgbU/Gt+OBJDHbIPZLzuOxsddXQ==; ipp_key=v1624185357165/v3394bd400b5e53a13cfc65163aeca6afa04ab3/ky10jxXvQ0B8Xo5Y8nWOSA==; __ddg1=S6D87mqsSCdqGZuP1mgM; __ddgid=noo4zt9Ka19uLm8P; __ddg2=PBAA857Z8o9hHZQt; __ddgmark=ccY74R9xz3Iq7H8F'
    response = requests.get(link, headers={'User-Agent': UserAgent().chrome,
                                           'Cookie': cookie})
    try:
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        err_code = str(http_err).split()[0]
        if err_code == '404':
            return None
        elif err_code == '403':
            sleeping_time = random.randint(2, 10)
            print(f'Site blocks requests. Sleeping for {sleeping_time} sec.')
            time.sleep(sleeping_time)
            return get_response(link)


def brandshop_scrapper():
    prepare_txt_files(f'{pass_to_project}brandshop_scrap.txt',
                      f'{pass_to_project}brandshop_scrap_old.txt')
    pages_to_scan = 5

    for page_num in range(1, pages_to_scan):
        brandshop_url = f'https://brandshop.ru/sale/?mfp=31-kategoriya[%D0%9A%D0%B5%D0%B4%D1%8B,%D0%9A%D1%80%D0%BE%D1%81%D1%81%D0%BE%D0%B2%D0%BA%D0%B8]&sort=p.price&order=DESC&limit=60&page={page_num}'

        brandshop_response = get_response(brandshop_url)

        if brandshop_response is None:
            break

        brandshop_sales_html = BeautifulSoup(brandshop_response.content)

        if brandshop_sales_html.find_all('div', 'row category-products') == []:
            break

        sneakers_html_block = \
            brandshop_sales_html.find_all('div', 'row category-products')[0]
        sneakers = sneakers_html_block.find_all('a', 'product-image')

        sneakers_names = [sneaker.next.next['alt'] for sneaker in sneakers]
        sneakers_links = [sneaker['href'] for sneaker in sneakers]
        sneakers_photo = [sneaker.next.next['data-rjs'] for sneaker in
                          sneakers]
        sneakers_prices_old = [
            price_block.text.split(' – ')[0][0:-1].replace(' ', '')
            for price_block in sneakers_html_block.find_all('div', 'price')]
        sneakers_prices = [price_block.text[0:-1].replace(' ', '')
                           for price_block in
                           sneakers_html_block.find_all('div', 'price-sale')]
        sneakers_sizes = []

        for link in tqdm(sneakers_links):
            response = get_response(link)
            item = BeautifulSoup(response.content, 'html.parser')
            size = item.find_all('div', 'product-size')[0].text.strip().split(
                '\n')
            sneakers_sizes.append(size)

        sneakers_types = []

        for sneaker_name in sneakers_names:
            if 'женск' in sneaker_name.lower():
                sneakers_types.append('woman')
            elif 'мужск' in sneaker_name.lower():
                sneakers_types.append('man')
            else:
                sneakers_types.append('unisex')

        add_sneakers_scrap(f'{pass_to_project}brandshop_scrap.txt',
                           sneakers_names, sneakers_links,
                           sneakers_photo, sneakers_prices_old,
                           sneakers_prices, sneakers_types, sneakers_sizes)


brandshop_scrapper()


# In[ ]:


def find_new_items_brandshop():
    open(f'{pass_to_project}new_items_brandshop.txt', 'w').close()
    new_items = open(f'{pass_to_project}new_items_brandshop.txt', 'w')

    bsh_file = open(f'{pass_to_project}brandshop_scrap.txt', 'r')
    sneakers = list(
        map(lambda x: x.split('\n'), bsh_file.read().strip().split('\n\n')))
    bsh_file.close()

    bsh_old_file = open(f'{pass_to_project}brandshop_scrap_old.txt', 'r')
    old_sneakers = list(map(lambda x: x.split('\n'),
                            bsh_old_file.read().strip().split('\n\n')))
    bsh_old_file.close()

    if sneakers == [['']]:
        return

    for sneaker in sneakers:
        sneaker_name = sneaker[0]
        sneaker_sizes = sneaker[-1].split(', ')

        for old_sneaker in old_sneakers:
            old_sneaker_name = old_sneaker[0]
            old_sneaker_sizes = old_sneaker[-1].split(', ')
            if sneaker_name == old_sneaker_name:
                for old_size in old_sneaker_sizes:
                    if old_size in sneaker_sizes:
                        sneaker_sizes.remove(old_size)
        if len(sneaker_sizes) != 0:
            new_items.write(sneaker_name + '\n')
            new_items.write(sneaker[1] + '\n')
            new_items.write(sneaker[2] + '\n')
            new_items.write(sneaker[3] + '\n')
            new_items.write(sneaker[4] + '\n')
            new_items.write(sneaker[5] + '\n')
            new_items.write(', '.join(sneaker_sizes) + '\n')
            new_items.write('\n')

    new_items.close()


find_new_items_brandshop()
find_new_items_brandshop()


def notify_about_item(sneaker):
    name = sneaker[0]
    link = sneaker[1]
    photo_link = sneaker[2]
    price = sneaker[4]
    model_type = sneaker[5]
    sizes = sneaker[6].split(', ')

    n = len(sizes)
    for i in range(n):
        size = sizes[i].split()[0]
        if len(size) > 2:
            sizes.append(size[:2] + ' EU+')
            sizes[i] = str(int(size[:2]) + 1) + ' EU-'

    groups = {'man': ['man', 'any'],
              'woman': ['woman', 'any'],
              'unisex': ['man', 'woman', 'any']
              }
    for group in groups[model_type]:
        for size in sizes:
            real_size = int(size.split()[0])

            if size[-1] == '-':
                real_size = real_size - 1 + 0.5
            elif size[-1] == '+':
                real_size += 0.5

            size = size.split()[0]
            users_id_txt = open(
                f'{pass_to_project}sought_for_items/{group}/{group}{size}.txt',
                'r')

            users_id = users_id_txt.read().strip().split('\n')
            users_id_txt.close()

            open(
                f'{pass_to_project}sought_for_items/{group}/{group}{size}.txt',
                'w').close()
            users_id_txt_new = open(
                f'{pass_to_project}sought_for_items/{group}/{group}{size}.txt',
                'w')

            for user_id in users_id:
                if user_id == '':
                    continue
                try:
                    bot.send_message(user_id, 'Доступен Ваш размер: ' + str(
                        real_size) + '\n\n'
                                     + name + '\n\n' + 'Цена: ' + price + '₽' + '\n' + link)
                    users_id_txt_new.write(user_id + '\n')
                    # time.sleep(1)
                except BaseException:
                    print(user_id, 'not sent')

            users_id_txt_new.close()


def notify_about_new_items_brandshop():
    new_items = open(f'{pass_to_project}new_items_brandshop.txt', 'r')
    sneakers = [sneaker_block.split('\n') for sneaker_block in
                new_items.read().strip().split('\n\n')]

    for sneaker in sneakers:
        if sneaker != ['']:
            notify_about_item(sneaker)
    new_items.close()


notify_about_new_items_brandshop()


# In[ ]:


def regular_update_and_notification():
    brandshop_scrapper()
    find_new_items_brandshop()
    notify_about_new_items_brandshop()


schedule.every().day.do(regular_update_and_notification)

while True:
    schedule.run_pending()
    time.sleep(1)
