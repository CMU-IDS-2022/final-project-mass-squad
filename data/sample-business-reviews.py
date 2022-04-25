import pandas as pd

df_business = pd.read_csv("~/Downloads/preprocess_business.csv")
df_business = df_business.head(100)

df_reviews = pd.read_csv("~/Downloads/preprocess_reviews.csv")

merged_df = df_business.join(df_reviews.set_index('business_id'), on='business_id', lsuffix='_business', rsuffix='_review')
print(merged_df.count())
merged_df.to_csv('merged_reviews.csv')
