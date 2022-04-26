import os
from tkinter import CENTER
from markdown import markdown
import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
from wordcloud import WordCloud
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from sklearn.feature_extraction._stop_words import ENGLISH_STOP_WORDS
import folium
from streamlit_folium import folium_static
import base64
from similarity.similarity import * 
from similarity_viz import *

from OverallView import overallVis
business_name = None


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
def load_reviews_without_text():
    return pd.read_csv("data/preprocess_reviews_no_text.csv")

merged_df = read_data()
obj = overallVis()

def welcome_page():
    st.markdown('<style>' + open('icons.css').read() + '</style>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: black;'>Let Reviews Take Your Business to the Next Level!</h2>",
                unsafe_allow_html=True)
    # st.markdown("![](/Users/malaika/Documents/CMU/Spring22/05-839/final-project-mass-squad/images/review.png)")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.image("images/review.png", width=250)

    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        st.markdown(
            "<p> Whether you're a <span style='color: #c21111'> restauranteur </span>, and <span style='color: "
            "#c21111'> entrepreneur </span> with the next big idea in the food business, "
            "or just a <span style='color: #c21111'> good 'ol food enthusiast </span> trying to find the best "
            "fries in town, we've got you "
            "covered!</p>", unsafe_allow_html=True)
        st.markdown(
            "<p> <span class='material-icons'> dinner_dining </span> <span style='color: #c21111'>Restaurant Owners "
            "</span>, if you're looking for ways to step up your "
            "game and get better reviews, you're in "
            "the right place! Study your reviews and ratings over time and checkout what your competition is doing to "
            "boost their reviews! </p>", unsafe_allow_html=True)

        st.markdown(
            "<p> <span class='material-icons'> brunch_dining </span>  <span style='color: #c21111'> Looking to start "
            "a restaurant? </span> Checkout the landscape of "
            "existing restaurants in your area to see if "
            "yours will be a good fit! Find out what features of a restaurant work in your neighborhood!</p>",
            unsafe_allow_html=True)

        st.markdown(
            "<p> <span class='material-icons'> fastfood </span>  <span style='color: #c21111'> Are you here to just "
            "find a place to grab a bite? </span> We've got "
            "your back! Discover the best restaurants in your area and see what fellow foodies have to say about "
            "it!</p>",
            unsafe_allow_html=True)


def specific_restaurant():
    all_business_ids = merged_df['name'].unique().tolist()

    '''
    ## Analyse your business with visualizations!
    '''
    feature_selectbox = st.selectbox("Select the name of your business", all_business_ids)

    my_business_df = merged_df[merged_df['name'] == feature_selectbox]
    positive_df = my_business_df[my_business_df['stars_review'] > 3]
    negative_df = my_business_df[my_business_df['stars_review'] < 2.5]
    #print(positive_df, negative_df)
    if not positive_df.empty and not negative_df.empty:
    ## WORDCLOUD FOR BOTH POSITIVE AND NEGATIVE REVIEWS
        stopword_set = set(stopwords.words('english') + list(ENGLISH_STOP_WORDS))
        full_text = ' '.join(positive_df['text'].dropna())
        cloud_no_stopword = WordCloud(background_color='white', stopwords=stopword_set,colormap='Greens', width=800, height=400, repeat=True).generate(full_text)
        neg_full_text = ' '.join(negative_df['text'].dropna())
        neg_cloud_no_stopword = WordCloud(background_color='white', stopwords=stopword_set,colormap='Reds', width=800, height=400, repeat=True).generate(neg_full_text)
        fig, ax = plt.subplots(1,2)
        ax[0].imshow(cloud_no_stopword, interpolation='bilinear')
        ax[0].axis('off')
        ax[1].imshow(neg_cloud_no_stopword, interpolation='bilinear')
        ax[1].axis('off')
        plt.show()
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()
    else:
        st.write('No reviews available for one of the word cloud columns please pick one which has reviews')


    '''
    ## STAR DISTRIBUTION
    '''    
    if st.checkbox("Show Star Rating Count"):
        df = my_business_df.rename(columns={'stars_review':'Count'})['Count'].value_counts()
        st.dataframe(df)
    distribution_df = my_business_df['stars_review'].value_counts().reset_index()
    
    distribution_df.rename(columns = {'stars_review':'Count', 'index':'Rating'}, inplace = True)
    
    reviews_cols_star = {'useful': {}}
    all_ratings = distribution_df['Rating'].tolist()
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
    return feature_selectbox


def display_graph(selection="Hello"):
    global business_name
    if "menu" in st.session_state:
        selection = st.session_state.menu
    if selection == 'Overall Landscape':
        st.title("Overall Landscape of restaurants")
        st.markdown("Hello Owner, The graphs below give an overview of how each of the categories impact the overall ratings distribution in case of all the restaurants in the dataset. \
            The ratings described here are mostly binary in terms of whether a restaurant has a certain facility or not, most cases having a certain facilities leads to a higher rating as compared to not having that. \
            The distribution of most graphs hover over 4 as the mean. \
            The overall idea is that you can compare and contrast the attributes that impact the ratings the most. \
            We also provide granularity in terms of state and city so you can focus on a specific state and city your restaurant is based out off. \
            The 0 label refers to the fact that the restaurant doesnt have a particular facility, as compared to 1 which means it suppports that particular facility")
        #obj.overall_view()
        obj.overall_bar()
    elif selection == "Your Restaurant":
        st.title("Analyse your own business!", anchor=CENTER)
        st.markdown('Hello Owner, we are displaying your reviews in the form of wordclouds from both the negative and positive reviews this gives you an idea as to your specific shortcomings and criticisms mentioned by the customers. It also gives you an idea as to what went well so you can continue with those practices. \
            The wordcloud we believe is helpful in highlighting the specific reasonings as to why your restaurant received low/high ratings. \
            Providing it time based granularity gives the you the option to specifically look at what went right and what went wrong during a particular time duration.\
            We also provide the you with visualizations that enable you to understand what attributes you lack that your competitors with better reviews exhibit as well as what attributes they share with competitors that have worse reviews.')
        business_name = specific_restaurant()
    elif selection == "Similarity Check":
        if business_name == None:
            all_business_ids = merged_df['name'].unique().tolist()
            feature_selectbox = st.selectbox("Select the name of your business", all_business_ids)
            business_name = feature_selectbox
        business_id = merged_df[merged_df['name'] == business_name]['business_id'].to_list()[0]
        print(business_id)
        generate_map_vis(business_id) 
    else:
        welcome_page()

st.session_state.mask = 'Hello'

selector = st.sidebar.selectbox(
    "Yelp Restaurant Analysis",
    ("Home", "Overall Landscape", "Your Restaurant", "Similarity Check"),
    on_change=display_graph(),
    key="menu",
)

#  ------------------- Top Bar details here ----------------------



