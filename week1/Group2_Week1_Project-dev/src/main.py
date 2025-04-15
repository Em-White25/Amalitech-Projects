from data_processing import load_data, clean_data, save_cleaned_data
from eda import show_basic_info, plot_correlation_matrix
from visualization import *
from model import train_model
from datetime import datetime

def main():
    # Step 1: Load & clean data
    df = load_data('data/raw/Titanic dataset.csv')
    df_cleaned = clean_data(df)
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    save_cleaned_data(df_cleaned, f'data/processed/cleaned_data_{timestamp}.csv')

    # Step 2: EDA & Visualizatio
    show_basic_info(df_cleaned)
    plot_correlation_matrix(df_cleaned)
    # Survival Rate by pclass
    plot_survival_rate(df_cleaned, 'pclass', 'Survival Rate by Passenger Class', 'Passenger Class', [1, 2, 3], ['1st', '2nd', '3rd'])

    # Survival Rate by sex
    plot_survival_rate(df_cleaned, 'sex', 'Survival Rate by Sex', 'Sex')

    # Survival Rate by embarked
    plot_survival_rate(df_cleaned, 'embarked', 'Survival Rate by Embarked Port', 'Embarked Port')

    # Age Distribution by Survival
    plot_numerical_distribution_by_survival(df_cleaned, 'age', 'Age Distribution by Survival', 'Age')

    # Fare Distribution by Survival (Histogram)
    plot_numerical_distribution_by_survival(df_cleaned, 'fare', 'Fare Distribution by Survival', 'Fare')

    # Fare Distribution by Survival (Box Plot)
    plot_boxplot_survival_by_numerical(df_cleaned, 'fare', 'Fare Distribution by Survival', 'Survived (0=No, 1=Yes)', 'Fare')

    # Survival Rate by pclass and sex
    plot_survival_rate_by_two_categorical(df_cleaned, 'pclass', 'sex', 'Survival Rate by Passenger Class and Sex', 'Passenger Class', x_ticks=[1, 2, 3], x_tick_labels=['1st', '2nd', '3rd'], hue_title='Sex')

    # Survival Rate by pclass and embarked
    plot_survival_rate_by_two_categorical(df_cleaned, 'pclass', 'embarked', 'Survival Rate by Passenger Class and Embarked Port', 'Passenger Class', x_ticks=[1, 2, 3], x_tick_labels=['1st', '2nd', '3rd'], hue_title='Embarked Port')

    # Survival Rate by sex and embarked
    plot_survival_rate_by_two_categorical(df_cleaned, 'sex', 'embarked', 'Survival Rate by Sex and Embarked Port', 'Sex', hue_title='Embarked Port')

    # Box Plots of Age by pclass and Survival
    plot_boxplot_numerical_by_categorical_survival(df_cleaned, 'pclass', 'age', 'Age Distribution by Passenger Class and Survival', 'Passenger Class', 'Age')

    # Box Plots of Fare by pclass and Survival
    plot_boxplot_numerical_by_categorical_survival(df_cleaned, 'pclass', 'fare', 'Fare Distribution by Passenger Class and Survival', 'Passenger Class', 'Fare')

    # Scatter Plot of Age vs. Fare, Colored by Survival
    plot_scatterplot_numerical_by_survival(df_cleaned, 'age', 'fare', 'Age vs. Fare, Colored by Survival', 'Age', 'Fare')
  

    # Step 3: Model training
    model = train_model(df_cleaned, target_column='survived')  

if __name__ == '__main__':
    main()