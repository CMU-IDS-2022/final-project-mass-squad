from markdown import markdown
import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
#from wordcloud import WordCloud
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from sklearn.feature_extraction._stop_words import ENGLISH_STOP_WORDS
import folium
from streamlit_folium import folium_static
import os
import base64
from similarity.similarity import * 

from OverallView import overallVis

PHOTO_DIR = "./data/yelp_photos/photos/"

st.set_page_config(layout="wide")

st.markdown(
    """<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    """,
    unsafe_allow_html=True)

st.sidebar.image("yelp-logo-vector.png", use_column_width=True, output_format="PNG")

import nltk
nltk.download('stopwords')
@st.cache
def read_data():
    merged_df = pd.read_csv('data/merged_reviews.csv')
    return merged_df

@st.cache
def load_data():
    """
    Write 1-2 lines of code here to load the data from CSV to a pandas dataframe
    and return it.
    """
    df_merged = pd.read_csv("./data/final_merged_review_photo_business.csv")
    return df_merged


@st.cache
def get_filtered_rows(df, df_cat, selected_category, selected_rating):
    """
    Implement a function that computes which rows of the given dataframe should
    be part of the slice, and returns a boolean pandas Series that indicates 0
    if the row is not part of the slice, and 1 if it is part of the slice.
    
    In the example provided, we assume genders is a list of selected strings
    (e.g. ['Male', 'Transgender']). We then filter the labels based on which
    rows have a value for gender that is contained in this list. You can extend
    this approach to the other variables based on how they are returned from
    their respective Streamlit components.
    """
    labels = pd.Series([True] * len(df), index=df.index)
    if selected_category:
        l = df_cat["business_id"][df_cat['categories'].isin(selected_category)].tolist()
        labels &= df['business_id'].isin(l)
    if selected_rating:
        labels &= df['stars'].between(selected_rating[0],selected_rating[1],inclusive='both')
    
    return labels


def plot_map(user_row, df, bounds = None):
    base_map = folium.Map(
    location=[user_row['latitude'], user_row['longitude']],height='100%', width = '100%',
    tiles='https://{s}.tile.jawg.io/jawg-streets/{z}/{x}/{y}{r}.png?access-token=1HxubgB7ToJiUX3kEi7hGfaFJoxPpDwExwEifjbBjcOXE7m0mLsvxzA7McLVTRbf',
    attr="Tiles Courtesy of Jawg Maps")

    if(bounds is None):
        sw = df[['latitude', 'longitude']].min().values.tolist()
        ne = df[['latitude', 'longitude']].max().values.tolist()
        bounds = [sw, ne]

    base_map.fit_bounds(bounds) 

    for i in range(0,len(df)):
        if(df.iloc[i]['business_id'] != user_row['business_id']):
            popup_content = get_popup_content(df.iloc[i])   
            folium.Marker(
                location=[df.iloc[i]['latitude'], df.iloc[i]['longitude']],
                tooltip="<b>"+df.iloc[i]['name']+"</b>",
                popup= popup_content
            ).add_to(base_map)

    popup_content = get_popup_content(user_row, seed="<h2>Your Restaurant!</h2>")   
    folium.Marker(
        location=[user_row['latitude'], user_row['longitude']],
        tooltip="<b>"+user_row['name']+"</b>",
        popup= popup_content,
        icon=folium.Icon(color="red")
    ).add_to(base_map)

    return base_map

def get_popup_content(row, seed=""): 
    photos = os.listdir(PHOTO_DIR)
    content = seed+"<h3>"+str(row["name"])+", "+str(row["city"])+", "+str(row["state"])+"</h3><hr><h4>"+str(row["categories"])+"</h4>" 
    if(str(row["photo_id"])+".jpg" in photos):
        # print(row["photo_id"])
        img_path = os.path.join(PHOTO_DIR,str(row["photo_id"])+".jpg")
        # if(os.path.isdir(img_path)):
        encoded = base64.b64encode(open(img_path, 'rb').read())
        content = content + '<img src="data:image/png;base64,{}" alt={} height=300 width=300><br><br>'.format(encoded.decode('UTF-8'),str(row['name']))

    content = content + "Average Stars: " +str(row["stars"])+"<br><br>Top Review: "+str(row["text"])
    iframe = folium.IFrame(content, width=350, height=400)
    popup = folium.Popup(iframe)
    return popup
  

def generate_map_vis(business_id):

    st.title("Map Plot of Competitor Yelp Restaurants")
    with st.spinner(text="Loading data..."):
        busi = load_data()

    user_row = busi[busi['business_id']==business_id]
    user_row = user_row.iloc[0]
    filter_option = st.radio("Compare To: ",["Similar Businesses in State","Businesses in the Same City"], index = 1)

    if(filter_option == "Similar Businesses in State"):
        df = similarity(business_id, busi, 50)
    else:
        CITY=user_row["city"]
        print(CITY)
        df = busi[busi["city"]==CITY][:50]

    df_cat = df[['business_id','categories']]
    df_cat['categories'] = df_cat['categories'].str.split(",")
    df_cat = df_cat.explode('categories')
    df_cat = df_cat[df_cat["categories"]!="Restaurants"]
        

    selected_category = st.multiselect("Category", df_cat['categories'].unique())
    selected_rating = st.slider("Average Rating",0,5,(1,4))

    print(selected_category)

    filters = get_filtered_rows(df, df_cat, selected_category, selected_rating)

    filters = df[filters]

    with st.spinner(text="Filtering Restaurant"):
        sw = df[['latitude', 'longitude']].min().values.tolist()
        ne = df[['latitude', 'longitude']].max().values.tolist()
        bounds = [sw,ne]
        base_map = plot_map(user_row, filters, bounds = bounds)
        folium_static(base_map)


merged_df = read_data()
obj = overallVis()

def welcome_page():
    if st.checkbox("Show Cleaned Data"):
        st.write("Cleaning involved splitting data by spaces, combining entires like 'tropical datastorm' that got split redundantly, formatting strings with extra quotes, and for pressure as the storm becomes a Hurricane the pressure drops to lowest possible levels thus we have filled the NaN with 0")
        st.write(merged_df)
        st.write(obj.df)


def specific_restaurant():
    all_business_ids = merged_df['name'].unique().tolist()

    '''
    ## Analyse your business with visualizations!
    '''
    feature_selectbox = st.selectbox("Select the name of your business", all_business_ids)

    my_business_df = merged_df[merged_df['name'] == feature_selectbox]

    ## WORDCLOUD
    #stopword_set = set(stopwords.words('english') + list(ENGLISH_STOP_WORDS))
    #full_text = ' '.join(my_business_df['text'].dropna())
    #cloud_no_stopword = WordCloud(background_color='white', stopwords=stopword_set, width=800, height=400, repeat=True).generate(full_text)
    #plt.imshow(cloud_no_stopword, interpolation='bilinear')
    #plt.axis('off')
    #plt.show()
    #st.set_option('deprecation.showPyplotGlobalUse', False)
    #st.pyplot()


    '''
    ## STAR DISTRIBUTION
    '''    
    if st.checkbox("Show Star Rating Count"):
        df = my_business_df.rename(columns={'stars_review':'Count'})['Count'].value_counts()
        st.dataframe(df)
    distribution_df = my_business_df['stars_review'].value_counts().reset_index()
    
    distribution_df.rename(columns = {'stars_review':'Count', 'index':'Rating'}, inplace = True)
    
    reviews_cols_star = {'useful': {}}
    all_ratings = [1, 2, 3, 4, 5]
    for rating in all_ratings:
        rating_df = my_business_df[my_business_df["stars_review"] == rating]
        useful_review = rating_df.reset_index().drop_duplicates(subset=["stars_review"])
        reviews_cols_star['useful'][rating] = useful_review['text'].item()
        

    star_useful = pd.DataFrame.from_dict(reviews_cols_star['useful'].items())
    
    star_useful.columns = ['Rating', 'Voted most useful review']
    
    star_useful.set_index('Rating', inplace=True)
    distribution_df.set_index('Rating', inplace=True)
    
    distribution_df = distribution_df.join(star_useful.astype(str))
    distribution_df.reset_index(inplace=True)
    
    distribution_chart = alt.Chart(distribution_df).mark_bar().encode(
    y=alt.Y('Count', title="Rating Count"),
    x=alt.X('Rating:N', title = "Star-rating"),
    tooltip=["Count","Voted most useful review"]
    ).properties(
        title="Star Rating Distribution",
        width=800,height=600

    ).interactive()
    st.altair_chart(distribution_chart)

    '''
    ## RATING OVER TIME
    '''
    my_business_df['date'] = pd.to_datetime(my_business_df['date'])
    date_df = my_business_df.groupby(my_business_df.date.dt.year).mean()
    if st.checkbox("Show Year-wise Average Star Rating"):
        st.dataframe(date_df['stars_review'])
    
    # get best and worst review for each year    
    all_years = date_df.index.values.tolist()#
    reviews_cols = {'useful': {}, 'best': {}, 'worst': {}}
    for year in all_years:
        year_df = my_business_df[my_business_df["date"].dt.year == year]
        useful_count = year_df['useful'].max()
        best_count = year_df['stars_review'].max()
        worst_count = year_df['stars_review'].min()
        useful_review = my_business_df[my_business_df['useful'] == useful_count].reset_index().drop_duplicates(subset=["useful"])
        useful_review['date'] = year
        best_review = my_business_df[my_business_df['stars_review'] == best_count].reset_index().drop_duplicates(subset=["stars_review"])
        worst_review = my_business_df[my_business_df['stars_review'] == worst_count].reset_index().drop_duplicates(subset=["stars_review"])
        reviews_cols['useful'][year] = useful_review['text'].item()
        reviews_cols['best'][year] = best_review['text'].item()
        reviews_cols['worst'][year] = worst_review['text'].item()

    most_useful_df = pd.DataFrame.from_dict(reviews_cols['useful'].items())
    most_useful_df.columns = ['Year', 'Voted most useful review']
    most_useful_df.set_index('Year', inplace=True)
    date_df = date_df.join(most_useful_df.astype(str))

    best_df = pd.DataFrame.from_dict(reviews_cols['best'].items())
    best_df.columns = ['Year', 'Most Positive Review']
    best_df.set_index('Year', inplace=True)
    date_df = date_df.join(best_df.astype(str))

    worst_df = pd.DataFrame.from_dict(reviews_cols['worst'].items())
    worst_df.columns = ['Year', 'Most Negative Review']
    worst_df.set_index('Year', inplace=True)
    date_df = date_df.join(worst_df.astype(str))

    date_df = date_df.reset_index()

    ratings_chart = alt.Chart(date_df).encode(
        x=alt.X('date:T', title="Year"),
        y=alt.Y('stars_review:Q', title = "Average Star rating from Reviews"),
        tooltip = ['stars_review', 'Voted most useful review', 'Most Positive Review', 'Most Negative Review']
    ).properties(
        title="Average Star Ratings over Time",
        width=800, 
        height=400
    )
    st.altair_chart((ratings_chart.mark_line() + ratings_chart.mark_point(filled=True, size=40)).interactive())



def display_graph(selection="Hello"):
    if "menu" in st.session_state:
        selection = st.session_state.menu
    if selection == 'Overall Landscape':
        st.title("Overall Landscape of restaurants")
        obj.overall_view()
    elif selection == "Your Restaurant":
        specific_restaraunt()
    elif selection == "Similarity Check":
        generate_map_vis("MTSW4McQd7CbVtyjqoe9mw") 
    else:
        st.title('Hello their welcome to our webpage')
        welcome_page()

st.session_state.mask = 'Hello'

selector = st.sidebar.selectbox(
    "Yelp Restaurant Analysis",
    ("Select One", "Overall Landscape", "Your Restaurant", "Similarity Check"),
    on_change=display_graph(),
    key="menu",
)

#  ------------------- Top Bar details here ----------------------



