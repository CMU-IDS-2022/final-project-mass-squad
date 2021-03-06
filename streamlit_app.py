import os
import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
import folium
import matplotlib.pyplot as plt
import base64
import nltk

from markdown import markdown
from wordcloud import WordCloud
from nltk.corpus import stopwords
from sklearn.feature_extraction._stop_words import ENGLISH_STOP_WORDS
from streamlit_folium import folium_static
from similarity.similarity import *
from similarity_viz import *

nltk.download('stopwords')

from OverallView import overallVis

business_name = None

st.set_page_config(layout="wide")

with st.sidebar:
    col1, col2, col3 = st.columns(3)
    with col2:
        st.image("images/restaurant.png", width=90, output_format="PNG")


@st.cache
def read_data():
    merged_df = pd.read_csv('data/merged_reviews_polarity.csv')
    return merged_df


@st.cache
def load_reviews_without_text():
    return pd.read_csv("data/preprocess_reviews.csv")


merged_df = read_data()
obj = overallVis()


def welcome_page():
    st.markdown("<h2 style='text-align: center; color: black;'>Let Reviews Take Your Business to the Next Level!</h2>",
                unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[1]:
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
    spec_col1, spec_col2, spec_col3 = st.columns([1, 7, 1])
    with spec_col2:
        st.title("Deep Dive into Your Business!")
        st.markdown(
            "<p> <span class='material-icons'> monitor_heart </span> You're here because you need to check the pulse "
            "of your business. Interested in what your customers have to say about your restaurant? Are they mad that "
            "you don't have free WiFi? Do they think your bread is stale? Do they love your new outdoor seating? </p>",
            unsafe_allow_html=True)
        st.markdown(
            "<p> <span class='material-icons'> thumbs_up_down </span> Use the visualizations on this page to study "
            "the kinds of reviews your restaurant attracts. You can "
            "also analyze the distribution of your ratings and how your ratings have changed over time </p>",
            unsafe_allow_html=True)

        st.markdown(
            "<p> <span class='material-icons'> rate_review </span> Use the wordcloud to understand what words are "
            "frequently used to describe experiences at your restaurant. Use the histogram and the line graph to "
            "study the distribution of ratings over time! Hover over these plots to see a sample of reviews!</p>",
            unsafe_allow_html=True)

        all_business_ids = merged_df['name'].unique().tolist()

        feature_selectbox = st.selectbox("Select the name of your business", all_business_ids)

        my_business_df = merged_df[merged_df['name'] == feature_selectbox]

        sentiment_range = st.slider('Select the sentiment range you wish to explore', -1.0, 1.0, (-0.5, 0.5))

        net_df = my_business_df[my_business_df['polarity'] > sentiment_range[0]]
        net_df = net_df[net_df['polarity'] < sentiment_range[1]]

        if not net_df.empty:
            stopword_set = set(stopwords.words('english') + list(ENGLISH_STOP_WORDS))
            full_text = ' '.join(net_df['text'].dropna())
            # negative sentiment
            if sentiment_range[1] < 0.5:
                cloud_no_stopword = WordCloud(background_color='white', stopwords=stopword_set, colormap='Reds',
                                              width=800, height=400, repeat=True).generate(full_text)
            # positive sentiment
            else:
                cloud_no_stopword = WordCloud(background_color='white', stopwords=stopword_set, colormap='Greens',
                                              width=800, height=400, repeat=True).generate(full_text)
            plt.imshow(cloud_no_stopword, interpolation='bilinear')
            plt.axis('off')
            plt.show()
            st.set_option('deprecation.showPyplotGlobalUse', False)
            st.pyplot()
        else:
            st.write('No reviews available for one of the word cloud columns please pick one which has reviews')

        if st.checkbox("Show Star Rating Count"):
            df = my_business_df.rename(columns={'stars_review': 'Count'})['Count'].value_counts()
            st.dataframe(df)
        distribution_df = my_business_df['stars_review'].value_counts().reset_index()

        distribution_df.rename(columns={'stars_review': 'Count', 'index': 'Rating'}, inplace=True)

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
            x=alt.X('Rating:N', title="Star-rating"),
            tooltip=["Count", "Voted most useful review"]
        ).properties(
            title="Star Rating Distribution",
            width=600

        ).interactive()
        st.altair_chart(distribution_chart)

        my_business_df['date'] = pd.to_datetime(my_business_df['date'])
        date_df = my_business_df.groupby(my_business_df.date.dt.year).mean()
        if st.checkbox("Show Year-wise Average Star Rating"):
            st.dataframe(date_df['stars_review'])

        # get best and worst review for each year
        all_years = date_df.index.values.tolist()  #
        reviews_cols = {'useful': {}, 'best': {}, 'worst': {}}
        for year in all_years:
            year_df = my_business_df[my_business_df["date"].dt.year == year]
            useful_count = year_df['useful'].max()
            best_count = year_df['stars_review'].max()
            worst_count = year_df['stars_review'].min()
            useful_review = my_business_df[my_business_df['useful'] == useful_count].reset_index().drop_duplicates(
                subset=["useful"])
            useful_review['date'] = year
            best_review = my_business_df[my_business_df['stars_review'] == best_count].reset_index().drop_duplicates(
                subset=["stars_review"])
            worst_review = my_business_df[my_business_df['stars_review'] == worst_count].reset_index().drop_duplicates(
                subset=["stars_review"])
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
            y=alt.Y('stars_review:Q', title="Average Star rating from Reviews"),
            tooltip=['stars_review', 'Voted most useful review', 'Most Positive Review', 'Most Negative Review']
        ).properties(
            title="Average Star Ratings over Time",
            width=600
        )
        st.altair_chart((ratings_chart.mark_line() + ratings_chart.mark_point(filled=True, size=40)).interactive())
        return feature_selectbox


def display_graph(selection="Hello"):
    global business_name
    st.markdown('<style>' + open('icons.css').read() + '</style>', unsafe_allow_html=True)
    if "menu" in st.session_state:
        selection = st.session_state.menu
    if selection == 'Overall Landscape':
        obj.write_text()
        obj.overall_bar()
    elif selection == "Your Restaurant":
        business_name = specific_restaurant()
    elif selection == "The Competition":
        cols = st.columns([1, 4, 1])
        cols[1].title("Check out the Competition!")
        cols = st.columns([1, 7, 1])
        with cols[1]:
            if business_name is None:
                all_business_ids = merged_df['name'].unique().tolist()
                feature_selectbox = st.selectbox("Select the name of your business", all_business_ids)
                business_name = feature_selectbox
        business_id = merged_df[merged_df['name'] == business_name]['business_id'].to_list()[0]
        df_reviews = load_reviews_without_text()
        generate_map_vis(business_id, df_reviews)

    elif selection == "Home":
        welcome_page()
    else:
        welcome_page()


st.session_state.mask = 'Hello'

selector = st.sidebar.selectbox(
    "",
    ("Home", "Overall Landscape", "Your Restaurant", "The Competition"),
    on_change=display_graph(),
    key="menu",
)

