from code_01_Search_scrapper import get_html
import datetime as dt
import csv
from bs4 import BeautifulSoup
from datetime import datetime
from multiprocessing import Pool
import re
import os

NOW           = dt.datetime.now()
DATAST_FOLDER = 'dataset//'
SPICS_FOLDER  = 'pictures//search_pics//'
DFILE_NAME    = 'recipe_details' + NOW.strftime('%m-%d-%Y') + '.csv'

def get_list_of_recipes():

	recipe_links = []
	chef_file = DATAST_FOLDER + 'chefkoch_search_page10-03-2017.csv'

	with open(chef_file, 'r') as f:
	     chefkoch = csv.reader(f)
	     for row in chefkoch:
	         try:
	         	recipe_links.append(row[-2])
	         except: 
	         	continue 

	return(recipe_links)

def get_stats(soup):

	stats = {}

	# number of reviews
	reviews = soup.find('div', id="recipe__rating").find('span', class_ = "rating__total-votes m-r-s").text
	stats['reviews'] = reviews

	# other statistics
	if reviews != '(0)':
	    stats_table = soup.find('div', id="recipe-statistic").find_all('table')[1].find_all('tr')[1:5]
	else:
		stats_table = soup.find('div', id="recipe-statistic").find_all('table')[0].find_all('tr')[1:5]

	for tr in stats_table:
	    stat_name  = tr.find_all('td')[0].text.strip()
	    stat_value = tr.find_all('td')[1].text.strip()
	    stats[stat_name] = stat_value
	
	return(stats)

def get_ingredients(soup):
    
    # get list of ingredients
    ingredient_list = []
    amounts_ingredients = soup.find('table', class_="incredients").find_all('tr')

    for tr in amounts_ingredients:
        td = tr.find_all('td')[1].text.strip().split(',')[0]
        td = re.sub('\(.*?\)','', td)
        ingredient_list.append(td)

    return(str.join('@', ingredient_list))

def get_tags(soup):

	tags = []
	tag_cloud = soup.find('ul', class_ = 'tagcloud').find_all('li')
	for li in tag_cloud:
	    tags.append(li.find('a').text.strip())
	
	return(str.join('@', tags))

def get_author_info(soup):

	author = {}

	author['author_registration_date'] = soup.find('div', class_="user-details").find('p').find('br').previous_sibling.strip()
	author['author_reviews'] = soup.find('div', class_="user-details").find('p').find('br').next_sibling.strip()

	return(author)



def get_recipe_info(url):


	html = get_html(url)
	try:
		soup = BeautifulSoup(html, 'lxml')

		# lists of tags and ingredients
		ingredient_list = get_ingredients(soup)
		tags = get_tags(soup)

		# to update dictionary
		stats = get_stats(soup)
		author_info = get_author_info(soup)

		# write to dictionary
		data = {'link' : url,
		        'ingredients' : ingredient_list,
		        'tags': tags}
		data.update(stats)
		data.update(author_info)

	except:
		data = ''
	
	# append to the file 
	write_recipe_details(data)

def write_recipe_details(data):
    dpath = DATAST_FOLDER + DFILE_NAME
    with open(dpath, 'a', newline='') as f:
        writer = csv.writer(f)

        try:
	        writer.writerow((data['link'],
	                                data['ingredients'],
	                                data['tags'],
	                                data['reviews'],
	                                data['Freischaltung:'],
	                                data['gedruckt:'],
	                                data['gespeichert:'],
	                                data['author_registration_date'],
	                                data['author_reviews']))
        except:
	        writer.writerow('')

def main():

	start_time = datetime.now()
	print(start_time)

	recipe_links = get_list_of_recipes()
	print(len(recipe_links)/100*18/3600)

	with Pool(15) as p:
		p.map(get_recipe_info, recipe_links)


	end_time = datetime.now()
	total = end_time - start_time
	print(total)








if __name__ == '__main__':
    main()
