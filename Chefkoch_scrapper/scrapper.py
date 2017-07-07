import requests
from bs4 import BeautifulSoup
from datetime import datetime
from multiprocessing import Pool
import csv
import urllib.request
import os

# print(os.getcwd())


# url = 'http://www.chefkoch.de/rs/s0g145/Brot-und-Broetchen-Rezepte.html'


def get_html(url):
    r = requests.get(url)
    return r.text

def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    total_pages = soup.find('div', class_='ck-pagination qa-pagination').find('a', class_='qa-pagination-pagelink-last').text

    return int(total_pages)

def write_to_recipes(data):
    with open('chefkoch.csv', 'a', newline='') as f:
        writer = csv.writer(f)

        writer.writerow((data['recipe_id'],
                                data['recipe_name'],
                                data['average_rating'],
                                data['stars_shown'],
                                data['votes'],
                                data['difficulty'],
                                data['preparation_time'],
                                data['date'],
                                data['link'],
                                data['has_picture']))

def get_picture_link(item):
    item_class = item.find('picture').find('img').get('class')
    if item_class == ['lazyload']:
        img_link = item.find('picture').find('img').get('data-srcset')
    else: 
        img_link = item.find('picture').find('source').get('srcset')
    return(img_link)

def get_front_page(html):

    soup = BeautifulSoup(html, 'lxml')

    lis = soup.find_all('li', class_="search-list-item")

    for index, li in enumerate(lis):

        # get recipe ID
        try:
            id_r = li.get('id')
        except:
            id_r = ''

        # save picture and if recipe has one
        try: 
            if li.find('picture') is not None:
                img_link = get_picture_link(li)
                img_name = 'pics/' + str(id_r) + '.jpg'
                urllib.request.urlretrieve(img_link, img_name)
                has_pic = 'yes'
            else: 
                has_pic = 'no'
        except:
            has_pic = ''

        # link to the full recipe info
        try:
            koch_url = 'http://www.chefkoch.de'
            link = koch_url + li.find('a').get('href')
        except:
            link = ''

        # name of the recipe
        try:
            name = li.find('div', class_='search-list-item-title').text.encode('latin-1').strip()
        except:
            name = ''

        # average number of stars for recipe
        try:
            stars = li.find('span', class_='search-list-item-uservotes-stars').get('title')
        except:
            stars = ''

        # number of stars shown near recipe
        try:
            stars_shown = li.find('span', class_='search-list-item-uservotes-stars').get('class')[1]
        except:
            stars_shown = ''

        # number of votes
        try:
            votes = li.find('span', class_='search-list-item-uservotes-count').text.strip()
        except:
            votes = ''

        # difficulty of the recipe
        try:
            difficulty = li.find('span', class_='search-list-item-difficulty').text.strip()

        except:
            difficulty = ''

        # time to prepare recipe
        try:
            preptime = li.find('span', class_='search-list-item-preptime').text.strip()
        except:
            preptime = ''

        # date of reipe published
        try:
            date = li.find('span', class_='search-list-item-activationdate').text.strip()
        except:
            date = ''

        # write to dictionary
        data = {'recipe_id' : id_r,
                'recipe_name' : name,
                'average_rating': stars,
                'stars_shown' : stars_shown,
                'votes' : votes,
                'difficulty' : difficulty,
                'preparation_time' : preptime,
                'has_picture' : has_pic,
                'date' : date,
                'link' : link}
        
        # append to the file 
        write_to_recipes(data)

def please_scrap(url):
    print(url)
    html = get_html(url)
    get_front_page(html) 






def main():

    web_url = 'http://www.chefkoch.de'
    os.chdir(r'C:\\Users\Natalia\Documents\Thesis\scrap_try')

    start = datetime.now()

    # Get necessary parts of URLs for all categories of recipes
    soup = BeautifulSoup(get_html('http://www.chefkoch.de/rezepte/kategorien/'), 'lxml')
    categories = soup.find_all('h2', class_="category-level-1")
    urls_categories = []
    for index, category in enumerate(categories):
        
        href = category.find('a').get('href')
        category_number = href.split('/')[2].split('g')[1]
        category_name   = href.split('/')[-1]
        
        link_part = 'g' + category_number + '/' + category_name
        urls_categories.append(link_part)
        
    print(urls_categories)

    start_url = 'http://www.chefkoch.de/rs/s'

    for category in urls_categories:

        category_url = start_url + '0o3' + category
        total_pages = get_total_pages(get_html(category_url))
        # print(start_url, total_pages)

        url_list = []
        for i in range(0, total_pages + 1):
        # for i in range(0, 10):
            
            url_to_scrap = start_url + str(i * 30) + 'o3' + category
            url_list.append(url_to_scrap)
            # print(url_to_scrap)
            # get_front_page(get_html(url_to_scrap))

        # print(url_list)

        with Pool(20) as p:
            p.map(please_scrap, url_list)

    end = datetime.now()
    total = end - start
    print(total)






if __name__ == '__main__':
    main()


