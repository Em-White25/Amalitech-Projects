from dotenv import load_dotenv
import os
import sys
import requests
import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt


# plot functions
 
def plot_data(df, kind='scatter', **kwargs):


    if kind == 'scatter':
        x_col = kwargs.get('x_col', 'budget_million_usd')
        y_col = kwargs.get('y_col', 'revenue_million_usd')
        title = kwargs.get('title', 'Revenue vs. Budget Trends')

        plt.figure(figsize=(9, 5))
        franchise = df[df['franchise'] != 'Standalone']
        standalone = df[df['franchise'] == 'Standalone']

        plt.scatter(franchise[x_col], franchise[y_col], color='green', alpha=0.6, label='Franchise')
        plt.scatter(standalone[x_col], standalone[y_col], color='red', alpha=0.6, label='Standalone')

        plt.title(title)
        plt.xlabel(x_col.replace('_', ' ').title())
        plt.ylabel(y_col.replace('_', ' ').title())

    elif kind == 'line':
        date_col = kwargs.get('date_col', 'release_date')
        metrics = kwargs.get('metrics', ['revenue_million_usd', 'budget_million_usd'])
        title = kwargs.get('title', 'Yearly Trends')
        ylabel = kwargs.get('ylabel', 'Value')

        df['year'] = pd.to_datetime(df[date_col]).dt.year
        yearly_metrics = df.groupby('year')[metrics].mean().reset_index()

        plt.figure(figsize=(9, 5))
        for col in metrics:
            plt.plot(yearly_metrics['year'], yearly_metrics[col], marker='o', label=f'Mean {col.replace("_", " ").title()}')

        plt.title(title)
        plt.xlabel('Year')
        plt.ylabel(ylabel)

    elif kind == 'bar':
        metrics = kwargs.get('metrics', ['revenue_million_usd', 'budget_million_usd'])
        group_col = kwargs.get('group_col', 'franchise')
        label1 = kwargs.get('label1', 'Franchise')
        label2 = kwargs.get('label2', 'Standalone')

        franchise = df[df[group_col] != 'Standalone'][metrics].mean()
        standalone = df[df[group_col] == 'Standalone'][metrics].mean()

        x = range(len(metrics))
        width = 0.35

        plt.figure(figsize=(7, 4))
        plt.bar([i - width / 2 for i in x], franchise.values, width, label=label1)
        plt.bar([i + width / 2 for i in x], standalone.values, width, label=label2)

        plt.title(f'{label1} vs. {label2} Comparison')
        plt.xlabel('Metric')
        plt.ylabel('Million USD')
        plt.xticks(x, [metric.replace('_', ' ').title() for metric in metrics])

    else:
        raise ValueError("Invalid plot type. Choose 'scatter', 'line', or 'bar'.")

    plt.legend()
    plt.grid(True)
    plt.show()


# how to use for Scatter plot 
#plot_data(df, kind='scatter', x_col='budget_million_usd', y_col='revenue_million_usd')

# Yearly trend line plot
#plot_data(df, kind='line', metrics=['budget_million_usd', 'revenue_million_usd'])

# Franchise vs standalone bar chart
#plot_data(df, kind='bar', metrics=['budget_million_usd', 'revenue_million_usd'])
