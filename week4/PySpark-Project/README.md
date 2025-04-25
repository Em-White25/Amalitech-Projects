During this phase **(STEP 1)** of the project, I extracted a list of movies using their movie IDs from **The Movie Database (*TMDB*)**. 

* The data was pulled using an API call to TMDB. All movies were extracted except one (movie_id = 0), because the ID did not exist at the endpoint. The data was pulled using the **extract_data()** function from the **fetch_data.py file**

* Having already worked with this dataset previously, I know how the data looks like, nested dictionaries and lists because it is a JSON file.

* I converted the extracted movies into a pandas dataframe **df_movies**. I explored the first two rows of the data to examine how it looks like. A few columns have the nested list and dictionaries structure.

* *df_movies* was exported into the *data/* directory as *raw_csv_data*, adding today's date.
