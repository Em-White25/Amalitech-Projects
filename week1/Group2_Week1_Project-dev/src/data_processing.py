import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

def load_data(path):
    return pd.read_csv(path)

def remove_duplicates(df):
    """Remove duplicate rows."""
    return df.drop_duplicates()

def drop_unwanted_columns(df, columns):
    """Drop specified columns if they exist."""
    return df.drop(columns=columns, errors='ignore')

def encode_gender(df):
    """Encode 'sex' column: male -> 0, female -> 1."""
    df['sex'] = df['sex'].map({'male': 0, 'female': 1})
    return df

def fill_missing_age(df):
    """Fill missing 'age' with mean age per 'pclass'."""
    df['age'] = df.groupby('pclass')['age'].transform(lambda x: x.fillna(np.ceil(x.mean())))
    return df

def fill_missing_fare(df):
    """Fill missing 'fare' with mean fare per 'pclass'."""
    df['fare'] = df.groupby('pclass')['fare'].transform(lambda x: x.fillna(x.mean()))
    return df

def fill_missing_embarked(df):
    """Fill missing 'embarked' values with mode."""
    df['embarked'] = df['embarked'].fillna(df['embarked'].mode()[0])
    return df

def round_fare(df):
    """Round fare values to 2 decimal places."""
    df['fare'] = df['fare'].round(2)
    return df

def round_age(df):
    """Round age values to the nearest integer, rounding up values < 1 to 1."""
    df['age'] = df['age'].apply(lambda x: int(np.ceil(x)) if x < 1 else round(x))
    return df

def clean_data(df):
    """Clean the data: remove duplicates, handle missing values, and encode categorical data."""
    df = remove_duplicates(df)
    df = drop_unwanted_columns(df, ['name', 'home.dest', 'cabin', 'ticket', 'sibsp', 'parch', 'boat', 'body'])
    df = encode_gender(df)
    df = fill_missing_age(df)
    df = fill_missing_fare(df)
    df = fill_missing_embarked(df)
    df = round_fare(df)
    df = round_age(df)
    return df

def save_cleaned_data(df, path):
    """Save cleaned data to a CSV file."""
    df.to_csv(path, index=False)
