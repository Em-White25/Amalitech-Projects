### This Python file contains the main functions for repititive codes in this project.

import pandas as pd
import numpy as np
import requests
import ast 
import os 
import sys
import matplotlib.pyplot as plt 

from dotenv import load_dotenv
from datetime import datetime



''' Function for API call and extraction'''

def extract_data(url, api_key, data_points):
	# create an empty list to hold fetched results
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