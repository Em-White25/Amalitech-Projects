## Group-2-week1

# PROJECT STRUCTURE
```
/project-name
│
├── /data
│   ├── raw/                  # Store the raw, unprocessed data here.
│   └── processed/            # Store cleaned/processed data here.
│
├── /notebooks                # Jupyter Notebooks for EDA, cleaning, and ML.
│   ├── data_cleaning.ipynb
│   ├── eda.ipynb
│   ├── model_training.ipynb
│   └── visualization.ipyn
│
├── /src                      # Python scripts for reusable functions.
│   ├── data_processing.py
│   ├── eda.py
|   ├── main.py
|   ├── model.py
|   ├── pipeline_unittest.py
|   ├── visualization.py
│   └── requirements.txt
│
├── /visualizations           # Store the visualizations or dashboard files.
│   └── visualizations.png

```
# Titanic Survival Prediction Analysis

## Project Overview
The objective of this project is to build a data processing and machine learning pipeline that takes raw Titanic passenger data, cleans it, performs exploratory data analysis (EDA), extracts useful features, trains a predictive model, and evaluates its performance. The pipeline is designed to be modular, ensuring efficient data handling and reusability.

## Dataset Information
The dataset contains information about passengers aboard the Titanic, one of the most famous datasets used in data science and machine learning. It was created to analyze and understand the factors that influenced survival rates during the tragic sinking of the RMS Titanic on April 15, 1912.

### Data Description
The dataset is widely used for predictive modeling and statistical analysis to determine which factors (such as socio-economic status, age, gender, etc.) were associated with a higher likelihood of survival. It contains **1,309 rows** and **14 columns**.

### Columns:
- **Pclass**: Ticket class indicating the socio-economic status of the passenger. It is categorized into three classes:
  - 1 = Upper
  - 2 = Middle
  - 3 = Lower
- **Survived**: A binary indicator that shows whether the passenger survived (1) or not (0) during the Titanic disaster. This is the target variable for analysis.
- **Name**: The full name of the passenger, including title (e.g., Mr., Mrs., etc.).
- **Sex**: The gender of the passenger, denoted as either male or female.
- **Age**: The age of the passenger in years.
- **SibSp**: The number of siblings or spouses aboard the Titanic for the respective passenger.
- **Parch**: The number of parents or children aboard the Titanic for the respective passenger.
- **Ticket**: The ticket number assigned to the passenger.
- **Fare**: The fare paid by the passenger for the ticket.
- **Cabin**: The cabin number assigned to the passenger, if available.
- **Embarked**: The port of embarkation for the passenger. It can take one of three values:
  - C = Cherbourg
  - Q = Queenstown
  - S = Southampton
- **Boat**: If the passenger survived, this column contains the identifier of the lifeboat they were rescued in.
- **Body**: If the passenger did not survive, this column contains the identification number of their recovered body, if applicable.
- **Home.dest**: The destination or place of residence of the passenger.

These descriptions provide a detailed understanding of each column in the Titanic dataset, offering insights into the demographic, travel, and survival-related information recorded for each passenger.

## Data Pipeline
The project follows a structured pipeline to process the data and build a predictive model:

1. ### **Data Cleaning:**
 * **Removed Duplicates:** Ensured all records were unique by dropping duplicate rows.
 * **Dropped Unnecessary Columns:** Columns such as `name`, `home.dest`, `cabin`, `ticket`, `sibsp`, `parch`, `boat`, and `body` were removed as they were not essential for analysis or had excessive missing data.
 * **Encoded Gender:** The `sex` column was converted to numerical values (`male` = 0, `female` = 1) for model compatibility.
 * **Handled Missing Values:**
  - `age`: Missing values were filled with the rounded mean age per passenger class (`pclass`).
  - `fare`: Missing values were replaced with the average fare per `pclass`.
  - `embarked`: Filled with the most frequent port of embarkation.
 * Rounded Fare: The `fare` column was rounded to two decimal places to improve readability.
 **Output**:
The cleaned dataset has been saved to `data/processed/final_titanic_data.csv` and is now ready for exploratory data analysis and modeling.
 * Scaling numerical features if necessary also applying encoding columns.

2. ### **Exploratory Data Analysis (EDA):**
   ***Key EDA Steps***
   * Loaded Cleaned Dataset: Used the processed Cleaned Titanic dataset cleaned by the Data Cleaning team.

   * Inspected Data Structure: Explored the dataset shape, column types, and missing values to ensure data integrity.

   * Visualized Survival by Gender:

   Plotted average survival rate by gender to highlight disparity in survival rates (with females more likely to survive).

   * Generated Correlation Heatmap:

   * Focused on key features: pclass, age, fare, sex_female, sex_male, and survived.

   * Observed moderate positive correlation between sex_female and survived, and negative correlation with pclass.

***Insights***
   * Gender and Survival: Women had a higher survival rate than men.

   * Passenger Class: Lower class (higher pclass value) correlated with lower survival rates.

   * Fare: Higher fares slightly correlated with higher chances of survival.

4. ### **Model Training:**
   In this project, we used a Random Forest Classifier to predict outcomes based on the dataset. The model was fine-tuned to find the optimal hyperparameters for better performance. The following sections summarize the results and the model's performance.
   * **Best Model Parameters:**
     The following hyperparameters were determined to be the best for the model after tuning:

      * max_depth: **None** (allows the trees to grow until all leaves are pure)

      * max_features: **'auto'** (uses the square root of the total number of features for each split)

      * min_samples_leaf: **4** (sets the minimum number of samples required to be at a leaf node)

      * min_samples_split: **2** (the minimum number of samples required to split an internal node)

      * n_estimators: **100** (the number of trees in the forest)
   These parameters were chosen to balance model performance and complexity, optimizing for accuracy and generalization.

   * **Model Performance:**
      * Best Cross-validation Accuracy:
   The model achieved a cross-validation accuracy of **79.19%**, which indicates that the model performs well on unseen data during the training process.

      * Accuracy on Test Data:
   The model achieved an overall accuracy of **73.78%** on the test set, meaning that it correctly predicted **73.78%** of the test cases.

   * **Confusion Matrix:**
   The confusion matrix shows the number of correct and incorrect predictions:
      
      [[149  34]  
      [ 52  93]]
      
      * True Negatives (TN): 149 — The model correctly predicted class '0' (negative cases).

      * False Positives (FP): 34 — The model incorrectly predicted class '1' when it was actually class '0'.

      * False Negatives (FN): 52 — The model incorrectly predicted class '0' when it was actually class '1'.

      * True Positives (TP): 93 — The model correctly predicted class '1' (positive cases).
   
   * **Classification Report:**
      The classification report provides detailed metrics for both classes (0 and 1). Here's the breakdown:
      
                                    precision    recall  f1-score   support

                           0       0.74      0.81         0.78          183
                           1       0.73      0.64         0.68          145

                         accuracy                        0.74           328
                         macro avg 0.74      0.73        0.73           328
                         weighted avg 0.74   0.74        0.74           328
      
      * Precision: The proportion of positive predictions that were actually correct. For class '0', precision is 0.74, meaning 74% of the predicted class '0' were correct. Similarly, for class '1', it’s 0.73.

      * Recall: The proportion of actual positive cases that were correctly identified. For class '0', recall is 0.81, meaning 81% of the actual class '0' were correctly predicted. For class '1', recall is 0.64.

      * F1-Score: The harmonic mean of precision and recall, providing a balance between the two. The F1-score for class '0' is 0.78, and for class '1', it's 0.68.

      * Accuracy: The overall correctness of the model, which is 73.78% on the test data.

      * Support: The number of occurrences of each class in the test set (183 for class '0' and 145 for class '1').
   
   * **Conclusion:**
      The Random Forest model performed well with an accuracy of **73.78%**, achieving a good balance between precision, recall, and F1-score, especially for class **'0'** (with a higher recall). The model shows its strength in predicting class **'0'** more accurately, but there is room for improvement in predicting class **'1'**, as indicated by the lower recall for this class.
      By fine-tuning the model parameters and adjusting for performance on both classes, the model can potentially be enhanced further, for example, by using techniques such as class balancing or experimenting with other machine learning models.

5. ### **Pipeline Automation:**
   - Integrating all steps into an automated script.
   - Ensuring reusability for different Titanic datasets.

## Running the Project
To execute the full pipeline, follow these steps:

1. Clone the repository:
   ```sh
   git clone https://github.com/Em-White25/Group2_Week1_Project.git
   cd titanic-survival-analysis
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the preprocessing and model training script:
   ```sh
   python src/main.py
   ```
4. Run unit tests to validate functionality:
   ```sh
   pytest src/pipeline_unittest.py
   ```

## Deliverables
- **Data Cleaning:** Processed dataset with handled missing values.
- **EDA:** Summary statistics and survival insights.
- **Machine Learning Model:** Trained classifier for survival prediction.
- **Model Evaluation:** Performance metrics (accuracy, precision, recall, F1-score).
- **Visualizations:** Key plots for data interpretation.
- **Documentation:** Full project workflow and test cases.
- **Automated Pipeline:** End-to-end script for data processing and prediction.
