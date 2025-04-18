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

