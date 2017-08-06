import pandas as pd
import datetime as dt
import base64
import csv
import numpy as np


def main():

	# load dataset to merge
	recipe_info = pd.read_csv('recipes_encode.csv', error_bad_lines=False, 
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

	search_page = pd.read_csv('chefkoch.csv', error_bad_lines=False, 
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

	# split cilums to extract information needed
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

	# drop old varibles
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
                 'date_y'], 
                axis = 1, 
                inplace=True) 

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

	# save the dataset
	recipes_df.to_csv('recipes_df.csv', sep = '\t', encoding='utf-8', index=False)




if __name__ == '__main__':
    main()
