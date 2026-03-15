import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("Setup successful!")

#load dataset

data = pd.read_csv("student-dataset.csv")

#for quick overview of the dataset
print(data.head())

# for more detailed information about the dataset
print(data.info())

# check for missing values
print(data.isnull().sum())

#for statistical summary of the dataset
print(data.describe())

# for visualizing the distribution of a numeric variable (e.g., "portfolio_rating")
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(8,5))
sns.histplot(data["portfolio_rating"], bins=20, kde=True)

plt.title("Distribution of Portfolio Ratings")
plt.show()


# for visualizing the relationship between two numeric variables (e.g., "portfolio_rating" and "coverletter_rating")
plt.figure(figsize=(8,5))
sns.scatterplot(x=data["portfolio_rating"], y=data["coverletter_rating"])

plt.title("Portfolio Rating vs Cover Letter Rating")
plt.show()




#for checking the column names and data types
print(data.columns)

data.columns = data.columns.str.strip()
data.columns = data.columns.str.replace(".", "_")
data.columns = data.columns.str.replace(" ", "_")

print(data.columns)

# for checking the first few rows of the dataset after cleaning column names
print(data.head())




# for visualizing the distribution of a numeric variable (e.g., "Math_Score")
plt.figure(figsize=(10,6))

numeric_data = data.select_dtypes(include="number")

sns.heatmap(numeric_data.corr(), annot=True, cmap="coolwarm")

plt.title("Correlation Heatmap")
plt.show()