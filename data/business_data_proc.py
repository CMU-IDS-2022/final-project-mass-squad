import pandas as pd

raw_business_df = pd.read_csv('yelp_business.csv')

#print(raw_business_df.head(5))

# entries in raw df => neighborhood is sparse (decide if needed)
#print(raw_business_df.count())

# filter 1: drop if any field is null 
cleaned_df = raw_business_df.dropna()

# filter 2: is_open = true
# only business open currently are relevant
# 20% businesses are closed
cleaned_df = cleaned_df[cleaned_df['is_open']==1]

# filter 3: business with very few reviews aren't relevant 
# get average of review_count to decide = 41
# max = 7000 min = 3
# threshold for drop = 10
# 30% open businesses have less than 6 reviews
#average = cleaned_df['review_count'].mean()
#count_max = cleaned_df['review_count'].max()
#count_min = cleaned_df['review_count'].min()
cleaned_df = cleaned_df[cleaned_df['review_count'] > 5]
#print(cleaned_df.count())

# categories contain restaurants
cleaned_df['is_restaurant'] = cleaned_df.apply(lambda row : True if "Restaurants" in row["categories"] else False, axis=1)
restaurants_df = cleaned_df[cleaned_df['is_restaurant'] == True]
restaurants_df = restaurants_df.drop(columns = ['is_restaurant'])

# final csv has businesses that include 'Restaurants' in categories
restaurants_df.to_csv('processed_business.csv')