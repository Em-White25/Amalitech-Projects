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

