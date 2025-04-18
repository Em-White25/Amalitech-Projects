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

