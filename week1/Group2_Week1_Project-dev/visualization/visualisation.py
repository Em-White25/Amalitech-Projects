import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns





def plot_survival_rate(df, x_col, title, x_label, x_ticks=None, x_tick_labels=None):
    sns.barplot(x=x_col, y='survived', data=df)
    plt.title(title)
    plt.ylabel('Survival Rate')
    plt.xlabel(x_label)
    if x_ticks and x_tick_labels:
        plt.xticks(x_ticks, x_tick_labels)
    plt.show()

def plot_survival_rate_by_two_categorical(df, x_col, hue_col, title, x_label, y_label='Survival Rate', x_ticks=None, x_tick_labels=None, hue_title=None):
    sns.catplot(x=x_col, y='survived', hue=hue_col, data=df, kind='bar')
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    if x_ticks and x_tick_labels:
        plt.xticks(x_ticks, x_tick_labels)
    if hue_title:
        plt.legend(title=hue_title)
    plt.show()

def plot_numerical_distribution_by_survival(df, num_col, title, x_label, y_label='Density'):
    sns.histplot(data=df, x=num_col, hue='survived', kde=True)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

def plot_boxplot_survival_by_numerical(df, num_col, title, x_label, y_label):
    sns.boxplot(x='survived', y=num_col, data=df)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

def plot_boxplot_numerical_by_categorical_survival(df, cat_col, num_col, title, x_label, y_label):
    sns.boxplot(x=cat_col, y=num_col, hue='survived', data=df)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

def plot_scatterplot_numerical_by_survival(df, x_col, y_col, title, x_label, y_label):
    sns.scatterplot(x=x_col, y=y_col, hue='survived', data=df)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

def plot_count(df, x_col, title, x_label):
    sns.countplot(x=x_col, data=df)
    plt.title(title)
    plt.xlabel(x_label)
    plt.show()

df_titanic = pd.read_csv('../data/processed/Cleaned_Titanic_Dataset.csv', index_col= "S/N")

# Survival Rate by pclass
plot_survival_rate(df_titanic, 'pclass', 'Survival Rate by Passenger Class', 'Passenger Class', [1, 2, 3], ['1st', '2nd', '3rd'])

# Survival Rate by sex
plot_survival_rate(df_titanic, 'sex', 'Survival Rate by Sex', 'Sex')

# Survival Rate by embarked
plot_survival_rate(df_titanic, 'embarked', 'Survival Rate by Embarked Port', 'Embarked Port')

# Age Distribution by Survival
plot_numerical_distribution_by_survival(df_titanic, 'age', 'Age Distribution by Survival', 'Age')

# Fare Distribution by Survival (Histogram)
plot_numerical_distribution_by_survival(df_titanic, 'fare', 'Fare Distribution by Survival', 'Fare')

# Fare Distribution by Survival (Box Plot)
plot_boxplot_survival_by_numerical(df_titanic, 'fare', 'Fare Distribution by Survival', 'Survived (0=No, 1=Yes)', 'Fare')

# Survival Rate by pclass and sex
plot_survival_rate_by_two_categorical(df_titanic, 'pclass', 'sex', 'Survival Rate by Passenger Class and Sex', 'Passenger Class', x_ticks=[1, 2, 3], x_tick_labels=['1st', '2nd', '3rd'], hue_title='Sex')

# Survival Rate by pclass and embarked
plot_survival_rate_by_two_categorical(df_titanic, 'pclass', 'embarked', 'Survival Rate by Passenger Class and Embarked Port', 'Passenger Class', x_ticks=[1, 2, 3], x_tick_labels=['1st', '2nd', '3rd'], hue_title='Embarked Port')

# Survival Rate by sex and embarked
plot_survival_rate_by_two_categorical(df_titanic, 'sex', 'embarked', 'Survival Rate by Sex and Embarked Port', 'Sex', hue_title='Embarked Port')

# Box Plots of Age by pclass and Survival
plot_boxplot_numerical_by_categorical_survival(df_titanic, 'pclass', 'age', 'Age Distribution by Passenger Class and Survival', 'Passenger Class', 'Age')

# Box Plots of Fare by pclass and Survival
plot_boxplot_numerical_by_categorical_survival(df_titanic, 'pclass', 'fare', 'Fare Distribution by Passenger Class and Survival', 'Passenger Class', 'Fare')

# Scatter Plot of Age vs. Fare, Colored by Survival
plot_scatterplot_numerical_by_survival(df_titanic, 'age', 'fare', 'Age vs. Fare, Colored by Survival', 'Age', 'Fare')

# Count Plots
plot_count(df_titanic, 'pclass', 'Passenger Count by Class', 'Passenger Class')
plot_count(df_titanic, 'sex', 'Passenger Count by Sex', 'Sex')
plot_count(df_titanic, 'embarked', 'Passenger Count by Embarked Port', 'Embarked Port')