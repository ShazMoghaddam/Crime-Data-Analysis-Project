# Crime Data Analysis (2020–Present)

## Project Summary

This project presents an end-to-end data science analysis of reported crime data from 2020 to the present. The objective is to demonstrate practical skills in data cleaning, exploratory data analysis (EDA), visualisation, and machine learning using a real-world, messy dataset.

The project is designed specifically as a **portfolio piece for junior data analyst / data scientist roles**, focusing on clarity, sound decision-making, and explainability rather than overly complex models.

---

## Objectives

* Clean and preprocess raw crime data
* Explore trends and patterns in crime over time
* Visualise insights using clear and interpretable charts
* Build and evaluate a simple machine learning model
* Communicate findings in a structured and professional manner

---

## Dataset

* **Source:** DATA.GOG/Crime data (2020–Present)
* [](https://catalog.data.gov/dataset/crime-data-from-2020-to-present)
* **Format:** CSV
* **Content:** Crime records including time-based and categorical attributes

The dataset contains missing values, categorical variables, and temporal information—making it well suited for demonstrating real-world data preparation and analysis skills.

---

## Skills Demonstrated

This project showcases the following skills:

### Data Handling & Cleaning

* Loading and inspecting large CSV files
* Handling missing values and duplicates
* Converting and engineering date/time features

### Exploratory Data Analysis (EDA)

* Univariate, bivariate, and temporal analysis
* Identifying trends and patterns in crime data
* Translating visual outputs into insights

### Data Visualisation

* Time series plots to analyse trends over years
* Bar charts to compare crime categories
* Clear labelling and presentation-focused visuals

### Machine Learning

* Framing a real-world problem as a classification task
* Feature selection and encoding
* Train/test split and model evaluation
* Model interpretation using feature importance

### Communication & Documentation

* Clear markdown structure
* Commented code for readability
* Professional, recruiter-friendly explanations

---

## Machine Learning Approach (Plain English)

**Problem:** Predict the type of crime based on when it occurred.

**Why this problem?**

* It is realistic and easy to understand
* It demonstrates classification without unnecessary complexity
* It focuses on reasoning and interpretation, not just accuracy

**Model Used:** Random Forest Classifier

**Evaluation Metrics Explained Simply:**

* **Accuracy:** How often the model predicts the correct crime type
* **Precision & Recall:** How well the model handles different crime categories
* **Confusion Matrix:** Shows where the model gets confused between crime types

The model is not intended for real-world deployment, but rather to demonstrate the full machine learning workflow.

---

## Key Insights

* Crime frequency varies noticeably by year and day of the week
* A small number of crime categories account for a large proportion of incidents
* Temporal features alone provide limited predictive power, highlighting the importance of location and contextual data

---

## Limitations

* Only time-based features were used in the model
* No geographic or socio-economic variables included
* Class imbalance may affect prediction quality
* Results should not be interpreted as actionable law enforcement guidance

---

## Future Work

* Incorporate location-based features
* Address class imbalance with sampling techniques
* Experiment with simpler and more advanced models
* Integrate external datasets (e.g. population or weather data)

---

## Repository Structure

```
├── data/
│   └── Crime_Data_from_2020_to_Present.csv
├── notebooks/
│   └── crime_data_analysis.ipynb
├── README.md
```

---

## How to Run

1. Clone this repository
2. Install required dependencies:

   ```
   pip install pandas numpy matplotlib seaborn scikit-learn
   ```
3. Open the notebook:

   ```
   jupyter notebook
   ```
4. Run all cells from top to bottom

---

## Final Notes

This project emphasises **clarity, structure, and practical reasoning**—qualities essential for data science roles. The focus is not on building the most complex model, but on demonstrating a complete and well-documented analytical process.
