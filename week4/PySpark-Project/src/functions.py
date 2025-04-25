
import os
import time
import json
from datetime import datetime
import requests
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, size, when, expr, concat_ws, to_date, year, split, explode, mean, sum as _sum, 
    count, array_contains, lower
)
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns



"""Function to create a Spark session"""
def create_spark_session(app_name):
    """Create and configure a Spark session"""
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.repl.eagerEval.enabled", True) \
        .getOrCreate()
    return spark



"""Function to fetch movie data from TMDB API using Spark"""
def extract_data(url, api_key, data_points, spark):
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

    # Convert to RDD and to DataFrame
    rdd = spark.sparkContext.parallelize([json.dumps(movie) for movie in movies])
    df = spark.read.json(rdd)

    return df



"""Function to clean the data. Covers all steps in the STEP 2"""
def clean_data(df):

    # Drop unused columns
    cols_to_drop = ['adult', 'imdb_id', 'original_title', 'video', 
                    'homepage','backdrop_path', 'origin_country']
    df = df.drop(*cols_to_drop)


    '''Parse JSON like fields'''
# genre
    df = df.withColumn("genres", concat_ws("|", expr("transform(genres, x -> trim(x.name))")))

    # belongs_to_collection
    df = df.withColumn("belongs_to_collection", col("belongs_to_collection.name"))

    # production_countries
    df = df.withColumn("production_countries", expr("array_join(array_sort(transform(production_countries, x -> trim(x.name))), '|')"))

    # production_companies
    df = df.withColumn("production_companies", expr("array_join(transform(production_companies, x -> x.name), '|')"))

    # spoken_languages
    df = df.withColumn("spoken_languages", expr("array_join(array_sort(transform(spoken_languages, x -> trim(x.english_name))), '|')"))

    '''Extract relevant info from credits'''
    # Get cast and cast size
    df = df.withColumn("cast", expr("array_join(transform(credits.cast, x -> x.name), '|')"))
    df = df.withColumn("cast_size", size("credits.cast"))

    # Get the crew size
    df = df.withColumn("crew_size", size("credits.crew"))

    # Extract the movie directors from the crew
    df = df.withColumn("director", expr("""
        CASE
            WHEN size(filter(credits.crew, x -> x.job = 'Director')) > 0
            THEN array_join(transform(filter(credits.crew, x -> x.job = 'Director'), x -> x.name), '|')
            ELSE NULL
        END
    """))

    # Drop credits column
    df = df.drop("credits")

    #round popularity and vote_average to 2 decimal places
    df = df.withColumn("popularity", expr("round(popularity, 2)"))
    df = df.withColumn("vote_average", expr("round(vote_average, 2)"))

    # Convert release_date to date type
    df = df.withColumn("release_date", to_date("release_date", "yyyy-MM-dd"))


    # Add new columns budget and revenue in million USD
    df = df.withColumn("budget_million_usd", expr("round(budget / 1e6, 2)"))
    df = df.withColumn("revenue_million_usd", expr("round(revenue / 1e6, 2)"))

  
  
    # Drop duplicates and filter final rows
    df = df.dropDuplicates()

    # Filter where status is not "Released"
    df = df.filter(col("status") == "Released").drop("status")

    # Reorder the columns
    df = df.select([
        "id", "title", "tagline", "release_date", "genres", "belongs_to_collection",
        "original_language", "budget_million_usd", "revenue_million_usd", "production_companies",
        "production_countries", "vote_count", "vote_average", "popularity", "runtime",
        "overview", "spoken_languages", "poster_path", "cast", "cast_size", "director", "crew_size"
    ])

    return df





"""Function to add KPI columns (profit and ROI) to the DataFrame."""
def kpi_indicators(df):
    
    df = df.withColumn("profit", expr("round(revenue_million_usd - budget_million_usd, 2)"))
    df = df.withColumn("roi", when(col("budget_million_usd") > 0, expr("round(revenue_million_usd / budget_million_usd, 2)")).otherwise(None))
    
    return df





"""Function to rank movies based on a specific column."""
def rank_movies_spark(df, sort_by, ascending=False, min_budget_million_usd=None, min_votes=None, top_n=3):
   
    ranked_df = df

    if min_budget_million_usd is not None:
        ranked_df = ranked_df.filter(col("budget_million_usd") >= min_budget_million_usd)

    if min_votes is not None:
        ranked_df = ranked_df.filter(col("vote_count") >= min_votes)

    order_col = col(sort_by).asc() if ascending else col(sort_by).desc()

    ranked_df = ranked_df.orderBy(order_col).select("title", sort_by).limit(top_n)

    return ranked_df



"""Function to search for movies starring a specific actor or genre."""
def search_movies(df, actors=None, genres=None, sort_by=None, ascending=False):

    if not actors and not genres:
        print("Please provide at least one actor or genre to search for.")
        return None

    query = df
    if genres:
        for genre in genres:
            query = query.filter(lower(col("genres")).contains(lower(genre)))

    if actors:
        # Use array_contains if 'cast' was an array, otherwise use string contains
        for actor in actors:
            query = query.filter(lower(col("cast")).contains(lower(actor)))

    if sort_by:
        order_col = col(sort_by).asc() if ascending else col(sort_by).desc()
        return query.orderBy(order_col)
    else:
        return query


def display_results(df, columns=["title"]):
    """Displays the specified columns of a DataFrame."""
    if df is not None:
        df.select(*columns).show(truncate=False)


"""Function to search for movies starring Bruce Willis"""
def bruce_willis_movie(df):

    query1 = df.filter(
        col("genres").contains("Science Fiction") &
        col("genres").contains("Action") &
        col("cast").contains("Bruce Willis")
    ).orderBy(col("vote_average").desc())

    return query1.select("title", "vote_average").show(truncate=False)



"""Function for movies with Uma T and directed by Quentin Tarantino"""
def uma_tarentino(df):

    query2 = df.filter(
        col("cast").contains("Uma Thurman") &
        col("director").contains("Quentin Tarantino")
    ).orderBy(col("runtime").asc())

    return query2.select("title", "runtime").show(truncate=False)


def franchise_vs_standalone_performance(df):

    df = df.withColumn("is_franchise", col("belongs_to_collection").isNotNull())

    # Group by is_franchise and calculate aggregates with rounding
    franchise_stats = df.groupBy("is_franchise").agg(
        expr("round(avg(revenue_million_usd), 2)").alias("avg_revenue_million_usd"),
        expr("round(percentile_approx(roi, 0.5), 2)").alias("median_roi"),
        expr("round(avg(budget_million_usd), 2)").alias("avg_budget_million_usd"),
        expr("round(avg(popularity), 2)").alias("avg_popularity"),
        expr("round(avg(vote_average), 2)").alias("avg_vote_average")
    )

    # Rename True/False as Franchise/Standalone
    franchise_stats = franchise_stats.withColumn(
        "is_franchise",
        when(col("is_franchise") == True, "Franchise").otherwise("Standalone")
    )
    return franchise_stats.orderBy("is_franchise").show(truncate=False)



"""Function to evaluate the most successful franchises"""
def successful_franchises(df, top_n=3):

    # Filter to only rows where 'belongs_to_collection' is not null
    franchise_success = df.filter(col("belongs_to_collection").isNotNull())

    # Group by the franchise name
    franchise_success = franchise_success.groupBy("belongs_to_collection").agg(
        count("id").alias("num_movies"),
        expr("round(sum(budget_million_usd), 2)").alias("total_budget_million_usd"),
        expr("round(mean(budget_million_usd), 2)").alias("avg_budget_million_usd"),
        expr("round(sum(revenue_million_usd), 2)").alias("total_revenue_million_usd"),
        expr("round(mean(revenue_million_usd), 2)").alias("avg_revenue_million_usd"),
        expr("round(mean(vote_average), 2)").alias("avg_vote_average")
    )

    # Sort by total revenue
    franchise_success = franchise_success.orderBy(col("total_revenue_million_usd").desc()).limit(top_n)

    return franchise_success.show(truncate=False)

from pyspark.sql.functions import col, count, sum as _sum, mean, expr



"""Function to evaluate the most successful directors"""
def successful_directors(df, top_n=3):
    
    directors_success = df.groupBy("director").agg(
        count("id").alias("num_movies"),
        expr("round(sum(budget_million_usd), 2)").alias("total_budget_million_usd"),
        expr("round(mean(budget_million_usd), 2)").alias("avg_budget_million_usd"),
        expr("round(sum(revenue_million_usd), 2)").alias("total_revenue_million_usd"),
        expr("round(mean(revenue_million_usd), 2)").alias("avg_revenue_million_usd"),
        expr("round(mean(vote_average), 2)").alias("avg_vote_average")
    )

    # Sort by average revenue
    directors_success = directors_success.orderBy(col("avg_revenue_million_usd").desc()).limit(top_n)

    return directors_success.show(truncate=False)



"""Function to plot revenue vs budget"""
def plot_revenue_vs_budget(df):
    """Plot Revenue vs Budget trends."""
    
    df = df.withColumn("release_year", year("release_date"))

    
    plot_df = df.select("budget_million_usd", "revenue_million_usd").toPandas()

    
    sns.set(style="whitegrid")


    plt.figure(figsize=(7, 4))
    sns.scatterplot(data=plot_df, x="budget_million_usd", y="revenue_million_usd")
    plt.title("Revenue vs Budget")
    plt.xlabel("Budget (Million USD)")
    plt.ylabel("Revenue (Million USD)")
    plt.xscale("log")
    plt.yscale("log")
    plt.grid(True, which="both", ls="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()



"""Function to plot ROI distribution by genre"""
def plot_roi_distribution_by_genre(df):

  
    df_split = df.withColumn("genres", split(col("genres"), r"\|"))

    
    df_exploded = df_split.withColumn("genre", explode(col("genres")))


    pandas_df = df_exploded.select("genre", "roi").toPandas()


    plt.figure(figsize=(7, 4))
    sns.boxplot(data=pandas_df, x='genre', y='roi')
    plt.title('ROI Distribution by Genre')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Return on Investment (ROI)')
    plt.grid(True, ls="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()



"""Function to plot popularity vs rating"""
def plot_popularity_vs_rating(df):

    pandas_df = df.select("vote_average", "popularity").toPandas()

    plt.figure(figsize=(7, 4))
    sns.scatterplot(data=pandas_df, x='vote_average', y='popularity')
    plt.title('Popularity vs Rating')
    plt.xlabel('Average Rating')
    plt.ylabel('Popularity')
    plt.grid(True, ls="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()



"""Function to plot Yearly Box Office trends"""
def plot_yearly_trends(df):

    df = df.withColumn("release_year", year(col("release_date")))


    revenue_per_year = df.groupBy("release_year").agg(
        mean("revenue_million_usd").alias("revenue_million_usd"),
        mean("budget_million_usd").alias("budget_million_usd"),
        mean("popularity").alias("popularity")
    )


    pandas_df = revenue_per_year.orderBy("release_year").toPandas()
    pandas_df.set_index("release_year", inplace=True)

    
    plt.figure(figsize=(7, 4))
    sns.lineplot(data=pandas_df, x=pandas_df.index, y="revenue_million_usd", label="Revenue")
    sns.lineplot(data=pandas_df, x=pandas_df.index, y="budget_million_usd", label="Budget")
    plt.title("Yearly Trends: Revenue and Budget")
    plt.xlabel("Year")
    plt.ylabel("Million USD")
    plt.legend()
    plt.grid(True, ls="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()




"""Function to plot Franchise vs Standalone Success"""
def plot_franchise_vs_standalone_success(df):

    df = df.withColumn("is_franchise", col("belongs_to_collection").isNotNull())

    #compute the mean of the KPIs for franchises and standalone movies
    franchise_vs_standalone = df.groupBy("is_franchise").agg(
        mean("revenue_million_usd").alias("revenue_million_usd"),
        mean("budget_million_usd").alias("budget_million_usd"),
        mean("popularity").alias("popularity"),
        mean("vote_average").alias("vote_average")
    )

    
    pandas_df = franchise_vs_standalone.toPandas()

    pandas_df["is_franchise"] = pandas_df["is_franchise"].map({True: "Franchise", False: "Standalone"})
    pandas_df.set_index("is_franchise", inplace=True)

   
    pandas_df[["revenue_million_usd", "budget_million_usd"]].plot(
    kind="barh", 
    figsize=(7, 4), 
    color=["#1f77b4", "#ff7f0e"]
    )
    plt.title("Franchise vs Standalone: Revenue and Budget Comparison")
    plt.ylabel("Million USD")
    plt.xticks(rotation=0)
    plt.grid(True, ls="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()


"""Function to visualize all plots"""
def visualize_movies(df):

    plot_revenue_vs_budget(df)
    plot_roi_distribution_by_genre(df)
    plot_popularity_vs_rating(df)
    plot_yearly_trends(df)
    plot_franchise_vs_standalone_success(df)