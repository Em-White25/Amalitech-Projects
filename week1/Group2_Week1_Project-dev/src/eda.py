import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder

def show_basic_info(df):
    print(df.info())
    print(df.describe())

def plot_correlation_matrix(df):
    # Convert categorical columns to numeric values
    label_encoder = LabelEncoder()
    df['embarked'] = label_encoder.fit_transform(df['embarked'])
    corr = df.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix')
    plt.show()
