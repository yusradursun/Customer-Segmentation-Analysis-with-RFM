###############################################################
# Customer Segmentation with RFM
###############################################################

# 1. Data Understanding
# 2. Data Preparation
# 3. Calculating RFM Metrics
# 4. Calculating RFM Scores
# 5. Creating & Analyzing RFM Segments


###############################################################
# 1. Data Understanding
###############################################################
import datetime as dt
import pandas as pd

# Set display options for Pandas
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None) - (Optional: Show all rows)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


df_ = pd.read_excel("C:\\Users\\User\\PycharmProjects\yusra\\2 CRM ANALYTICS\\online_retail_II.xlsx",
                    sheet_name="Year 2009-2010")
df = df_.copy()


# Display the first few rows of the DataFrame
df.head()

# Show the shape of the DataFrame (number of rows and columns)
# output: (525461 - observation units, 8 - variables)
df.shape

# Display summary statistics of the dataFrame
df.describe().T

# Check for missing values in the dataFrame and sum them up
df.isnull().sum()

# Count the number of unique classes in the "Description" column
df["Description"].nunique()

# Show how many times each product description appears in the dataset (top 5)
df["Description"].value_counts().head()

# Identify the most frequently ordered product
df.groupby("Description").agg({"Quantity": "sum"}).head()

# Sort products by quantity sold in descending order
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

# Count unique invoices in DataFrame
df["Invoice"].nunique()


# Calculate the total price
df["TotalPrice"] = df["Quantity"] * df["Price"]

# Sum total prices by invoice
df.groupby("Invoice").agg({"TotalPrice": "sum"}).head()


###############################################################
# 2. Data Preparation
###############################################################

df.shape
df.isnull().sum()
df.describe().T
df = df[(df['Quantity'] > 0)]

# Remove missing values
df.dropna(inplace=True)

# Filter out canceled transactions.
df = df[~df["Invoice"].str.contains("C", na=False)]

###############################################################
# 3. Calculating RFM Metrics
###############################################################

df.head()

# Find the maximum invoice date
df["InvoiceDate"].max()

# Add 2 days to the latest invoice date for Recency.
today_date = dt.datetime(2010, 12, 11)
type(today_date)

# Create RFM metrics: Calculate Recency, Frequency, and Monetary metrics for each customer
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.head()

# Rename the columns
rfm.columns = ['recency', 'frequency', 'monetary']

# Describe the RFM metrics: Provide summary statistics for the RFM metrics
rfm.describe().T

# Filter for positive monetary values: Keep rows where the "monetary" value is greater than zero
rfm = rfm[rfm["monetary"] > 0]

# Display the shape of the resulting DataFrame:
rfm.shape



###############################################################
# 4. Calculating RFM Scores
###############################################################


rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])


rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

# The "rank" method is used to assign unique ranks to values in the "frequency" variable, avoiding ties or duplicates.
# This ensures that customers with the same frequency are not grouped together when dividing the data into quantiles.

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

# To create a composite score, the "RFM_SCORE"
# combines the Recency and Frequency values into a two-dimensional
# representation by converting them to strings and concatenating them.
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.describe().T

# Call the segment known as Champions
rfm[rfm["RFM_SCORE"] == "55"]

# Call the segment known as At Risk
rfm[rfm["RFM_SCORE"] == "11"]

###############################################################
# 5. Creating & Analysing RFM Segments
###############################################################

# Define the mapping of RFM score combinations to descriptive customer segments
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

# Create a new column "segment" in the RFM DataFrame based on RFM scores and the defined mapping
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

# Calculate and compare the mean values of recency, frequency, and monetary for each customer segment
segment_metrics = rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

# Display the top customers in the "cant_loose" segment
top_cant_loose_customers = rfm[rfm["segment"] == "cant_loose"].head()

# Create a new DataFrame to store information about new customers
new_df = pd.DataFrame()

# Select and store the customer IDs of customers in the "new_customers" segment
new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customers"].index

# Convert decimal values to integers
new_df["new_customer_id"] = new_df["new_customer_id"].astype(int)

# Export the new customer data to a CSV file
new_df.to_csv("new_customers.csv")

# Export the RFM data to a CSV file
rfm.to_csv("rfm.csv")
