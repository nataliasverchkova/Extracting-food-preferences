import pandas as pd
import datetime as dt
import base64
import csv
import numpy as np

NOW           = dt.datetime.now()
DATAST_FOLDER = 'dataset//'
FILE_NAME     = 'chefkoch_search_page' + NOW.strftime('%m-%d-%Y') + '.csv'
DFILE_NAME    = 'recipe_details' + NOW.strftime('%m-%d-%Y') + '.csv'
FFILE_NAME    = 'recipes_df' + NOW.strftime('%m-%d-%Y') + '.csv'

def main():

	# load dataset to merge
	dpath = DATAST_FOLDER + DFILE_NAME
	recipe_info = pd.read_csv(dpath, error_bad_lines=False, 
		                                            encoding='latin-1', 
		                                            header = None, 
		                                            usecols = [0, 1, 2, 3, 4, 5, 6, 7, 8],
                                                    names=['link', 
                                                           'ingredients', 
                                                           'tags', 
                                                           'reviews',
                                                           'date',
                                                           'printed',
                                                           'saved',
                                                           'author_reg_date',
                                                           'author_reviews'])

	dpath = DATAST_FOLDER + FILE_NAME
	search_page = pd.read_csv(dpath, error_bad_lines=False, 
		                                      encoding='latin-1', 
		                                      header = None, 
		                                      usecols = [0, 2, 3, 4, 5, 6, 7, 8, 9],
		                                      names=['recipe_id', 
		                                             'average_rating', 
		                                             'stars_shown', 
		                                             'votes',
		                                             'difficulty',
		                                             'preparation_time',
		                                             'date',
		                                             'link',
		                                             'has_picture'])

	# merge by  recipe link
	recipes_df = pd.merge(search_page, recipe_info, how = 'inner', on = ['link'])

	# drop NAs
	recipes_df = recipes_df.dropna()

	# split colunms to extract information needed
	recipes_df = pd.concat([recipes_df, 
                        recipes_df['average_rating'].str.split(expand=True)[[0, 4]] 
                              .rename(columns={0:'num_reviews', 4:'avg_rating'}), 
                        recipes_df['stars_shown'].str.split('-', expand=True)[[1]] 
                              .rename(columns={1:'stars'}), 
                        recipes_df['preparation_time'].str.split(' ', expand=True)[[0]] 
                              .rename(columns={0:'prep_time'}), 
                        recipes_df['printed'].str.split(expand=True)[[0, 1]] 
                              .rename(columns={0:'printed_total', 1:'printed_last_month'}), 
                        recipes_df['saved'].str.split(expand=True)[[0, 1]] 
                              .rename(columns={0:'saved_total', 1:'saved_last_month'}), 
                        recipes_df['author_reg_date'].str.split(expand=True)[[2]] 
                              .rename(columns={2:'author_registered'}), 
                        recipes_df['author_reviews'].str.split(expand=True)[[0]] 
                              .rename(columns={0:'author_posts'})], 
          axis = 1)

	# delete ()* around the numbers
	recipes_df[['saved_last_month', 'printed_last_month']] = \
	recipes_df[['saved_last_month', 'printed_last_month']].apply(lambda x: x.str.replace(r'[(,),\*]', ''))

	# delete . in numbers
	recipes_df[['num_reviews', 'printed_total', 'printed_last_month', 'saved_total', 'saved_last_month','author_posts']] = \
	(recipes_df[['num_reviews', 'printed_total', 'printed_last_month', 'saved_total', 'saved_last_month','author_posts']]
		       .apply(lambda x: x.str.replace('.', '')))


	# calculate the number of days recipe and author are on the website
	now = dt.datetime.now()	
	recipes_df['date_x'] = pd.to_datetime(recipes_df['date_x'], format = "%d.%m.%Y", errors='coerce')
	recipes_df['author_registered'] = pd.to_datetime(recipes_df['author_registered'], format = "%d.%m.%Y", errors='coerce')

	recipes_df['days_exists'] = recipes_df['date_x'].apply(lambda x: (now - x).days)
	recipes_df['author_reg']  = recipes_df['author_registered'].apply(lambda x: (now - x).days)


	# logarithm of how many times recipe was printed, saved per day - popularity metric; log of posts per day 
	recipes_df['printed_per_day'] = np.log(recipes_df['printed_total'].astype(float) / recipes_df['days_exists'])
	recipes_df['saved_per_day'] = np.log(recipes_df['saved_total'].astype(float) / recipes_df['days_exists'])
	recipes_df['posts_per_day'] = np.log(recipes_df['author_posts'].astype(float) / recipes_df['author_reg'])

	# change variables types
	category_cols = ['difficulty', 'has_picture', 'stars']
	date_cols     = ['date_x', 'author_registered']     
	numeric_cols  = ['num_reviews','avg_rating','prep_time','printed_total','printed_last_month','saved_total','saved_last_month','author_posts']

	recipes_df[category_cols] = recipes_df[category_cols].apply(lambda x: x.astype('category'))
	recipes_df[numeric_cols]  = recipes_df[numeric_cols].apply(lambda x: x.astype('float'))
	recipes_df[date_cols] = recipes_df[date_cols].apply(lambda x: x.astype('datetime64[ns]'))

	# create nested lists in the columns with ingredients and tags
	recipes_df[['tags']] = recipes_df[['tags']].apply(lambda x: x.str.replace(r'[\[\]]', ''))
	recipes_df[['ingredients']] = recipes_df[['ingredients']].apply(lambda x: x.str.replace(r'[\[\]]', ''))

	recipes_df['tags'] = [x.split("@") for x in recipes_df['tags']]
	recipes_df['ingredients'] = [x.split("@") for x in recipes_df['ingredients']]


	# for ingredients choose only those that are most frequent
	ingredients_list = []
	for ingredient_set in recipes_df['ingredients']:
	    for ingredient in ingredient_set:
	        ingredients_list.append(ingredient)

	ingredients_list = (pd.DataFrame(pd.Series(ingredients_list).value_counts())
	                    .reset_index()
	                    .rename(columns = {'index':'ingredient',
	                                       0:'freq'})
	                    .assign(perc = lambda df: df.freq / df.shape[0])
	                    .query('perc >= 0.03'))

	recipes_df['ingredients_short'] = (recipes_df['ingredients']
		.apply(lambda x: [item for item in x if item in list(ingredients_list['ingredient'])]))


	# create dummies from nested list of tags and modified list of ingredients
	ing_d = recipes_df['ingredients_short'].str.join('@').str.get_dummies('@').add_suffix('_ing')
	tag_d = recipes_df['tags'].str.join('@').str.get_dummies('@').add_suffix('_tag')

	recipes_df = pd.concat([recipes_df, 
	                        ing_d,
	                        tag_d],
	             axis = 1)


	# drop varibles that are not needed
	recipes_df.drop(['average_rating', 
                 'stars_shown', 
                 'votes', 
                 'preparation_time',
                 'link', 
                 'reviews', 
                 'printed',
                 'saved',
                 'author_reg_date', 
                 'author_reviews',
                 'date_y',
                 'tags',
                 'ingredients',
                 'ingredients_short'], 
                axis = 1, 
                inplace=True) 


	# save the dataset
	fpath = DATAST_FOLDER + FFILE_NAME
	recipes_df.to_csv(fpath, sep = '\t', encoding='utf-8', index=False)




if __name__ == '__main__':
    main()
