# Import packages all necessary packages
from dotenv import load_dotenv
import os
import sys
import requests
import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
'''
	This python file contains all the necessary functions for 
	* API extraction
	* Data cleaning and Transformation processes
	* Analytical functions for insights
	* functions for visualizations
'''

# STEP 1

'''
	Create an ectract funtion to extract API data from the endpoint.
	The function takes takes argument
	* set of data points to extract (eg. movie_ids)
	* takes the base url
	* It returns a list of data generated. (eg. list of movies) 
'''

#extracts api data
def api_extract(url, api_key, data_points):
	# create an empty list to hold fetched data results
	movies = []

	for movie_id in data_points:
		try:
			response = requests.get(f"{url}/{movie_id}?api_key={api_key}&append_to_response=credits")
			response.raise_for_status()  # Raise an error for bad responses (404 etc.)
			movie_data = response.json()
			movies.append(movie_data)
			print(f"[INFO] Fetched movie ID {movie_id} successfully.")
		except requests.exceptions.HTTPError as http_err:
			print(f"[WARNING] HTTP error for movie ID {movie_id}: {http_err}")
		except requests.exceptions.RequestException as req_err:
			print(f"[ERROR] Request error for movie ID {movie_id}: {req_err}")
		except Exception as e:
			print(f"[ERROR] Unexpected error for movie ID {movie_id}: {e}")

	return movies


# STEP 2
	"""
	Extracts data from a stringified dictionary or list of dictionaries in a DataFrame row.

	Parameters:
	- row: The DataFrame row being processed.
	- column_name (str): The column from which to extract the data.
	- key_name (str): The key to extract from the dictionary or each dictionary in a list. Default is 'name'.
	- is_list (bool): Set to True if the column contains a list of dictionaries. Default is False.
	- separator (str): The separator used to join values when is_list is True. Default is '|'.

	Returns:
	- A string value extracted from the dictionary or joined string of values from a list of dictionaries.
	  Returns an empty string if extraction fails or input is invalid.
	"""

#extracts data from nested columns
def extract_from_column(row, column_name, key_name='name', is_list=False, separator='|'):

	try:
		if pd.notna(row[column_name]):
			# Safely evaluate the string to a Python object (dict or list)
			parsed = ast.literal_eval(row[column_name])

			# If it's a list of dictionaries, extract and join the values
			if is_list and isinstance(parsed, list):
				return separator.join(item.get(key_name, '') for item in parsed)

			# If it's a single dictionary, return the value for the specified key
			elif isinstance(parsed, dict):
				return parsed.get(key_name, '')
	except (ValueError, SyntaxError, TypeError):
		pass

	return None 




	# Extract credits information
def extract_credits(row):
	try:
		if pd.notna(row['credits']):
			# Convert string to dictionary
			credits_dict = ast.literal_eval(row['credits'])
			
			# Get cast members (top 10 by order)
			cast = sorted(credits_dict.get('cast', []), key=lambda x: x.get('order', float('inf')))[:10]
			main_cast = "|".join([actor['name'] for actor in cast])
			
			# Get cast size
			cast_size = len(credits_dict.get('cast', []))
			
			# Get crew size
			crew_size = len(credits_dict.get('crew', []))
			
			# Get directors
			crew = credits_dict.get('crew', [])
			directors = "|".join([member['name'] for member in crew if member.get('job') == 'Director'])
			
			return pd.Series({
				'cast_size': cast_size,
				'crew_size': crew_size,
				'directors': directors,
				'cast': main_cast
			})
	except:
		pass
	return pd.Series({
		'cast_size': 0,
		'crew_size': 0,
		'directors': "",
		'cast': ""
	})



'''
	Function to drop columns
'''
def drop_columns(df, cols):

	df = df.drop(columns=cols)



'''
	Function to convert columns to millions usd
'''
def convert_to_millions(df, cols):

	for col in cols:
		df[f'{col}_million_usd'] = (df[col]/1e6).round(2)


'''
	Function to convert object to datetime
'''
def convert_datetime(df, cols):

	for col in cols:
		df[col] = pd.to_datetime(df[col], errors='coerce')


'''
	Function to round up numbers to 2 decimal places
'''
def round_to_two(df, cols):

	for col in cols:
		df[col] = df[col].round(2)


'''
	Function for renaming columns
'''
'''
def rename_column(df, old_col, new_col):
	for col in col:
		df[new_col] = df[old_col]
'''


#STEP 3 - Advanced Filtering
"""
	Filters and sorts a movie DataFrame based on optional search criteria.

	Parameters:
	----------
	df : pandas.DataFrame
		The DataFrame containing movie data.
	actor : str, optional
		Filter movies by actor name (case-insensitive).
	director : str, optional
		Filter movies by director name (case-insensitive exact match).
	genres : list of str, optional
		Filter movies that contain all specified genres (case-insensitive).
	franchise : str, optional
		Filter movies that belong to a specific franchise (case-insensitive).
	sort_by : str, default='runtime'
		Column name to sort the filtered results by.
	ascending : bool, default=True
		Whether to sort in ascending (True) or descending (False) order.

	Returns:
	-------
	pandas.DataFrame
		A DataFrame of movies matching the given criteria, sorted as specified.
	"""
# filter by actor    
def filter_and_sort_movies(
	df,
	actor=None,
	director=None,
	genres=None,
	franchise=None,
	sort_by=None,
	ascending=True):

	filtered_df = df.copy()

	if actor:
		filtered_df = filtered_df[filtered_df['cast'].str.contains(actor, case=False, na=False)]

	if director:
		filtered_df = filtered_df[filtered_df['directors'].str.lower() == director.lower()]

	if genres:
		for genre in genres:
			filtered_df = filtered_df[filtered_df['genres'].str.contains(genre, case=False, na=False)]

	if franchise:
		filtered_df = filtered_df[filtered_df['franchise'].str.contains(franchise, case=False, na=False)]

	return filtered_df.sort_values(by=sort_by, ascending=ascending)


	"""
		Compare a numeric column between franchise and standalone movies.

		Parameters:
		----------
		df : pandas.DataFrame
			The DataFrame containing movie data.
		column : str
			The column to calculate statistics on (must be numeric).
		agg : str, default='mean'
			The aggregation method to use: 'mean', 'median', or any valid pandas method.

		Returns:
		-------
		dict
			A dictionary with the aggregated values for franchise and standalone movies.
		"""

def compare_franchise_vs_standalone(df, column, agg='mean'):
 
	franchise_group = df[df['franchise'] != 'Standalone'][column]
	standalone_group = df[df['franchise'] == 'Standalone'][column]

	return {
		'franchise': getattr(franchise_group, agg)(),
		'standalone': getattr(standalone_group, agg)()
	}



