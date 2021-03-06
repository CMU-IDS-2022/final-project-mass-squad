from markdown import markdown
import numpy as np
import streamlit as st
import pandas as pd
import altair as alt

import folium
from streamlit_folium import folium_static
import os
import base64
from similarity.similarity import *

PHOTO_DIR = "./data/yelp_photos/photos/"


@st.cache
def load_data():
    """
    Write 1-2 lines of code here to load the data from CSV to a pandas dataframe
    and return it.
    """
    df_merged = pd.read_csv("./data/final_merged_review_photo_business.csv")
    return df_merged


@st.cache
def get_filtered_rows(df, df_cat, selected_category, selected_rating, main_id):
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
        labels &= df['stars'].between(selected_rating[0], selected_rating[1], inclusive='both')

    labels |= (df['business_id'] == main_id)

    return labels


def plot_map(user_row, df, df_reviews, bounds=None):
    base_map = folium.Map(
        location=[user_row['latitude'], user_row['longitude']],
        tiles='https://{s}.tile.jawg.io/jawg-streets/{z}/{x}/{y}{'
              'r}.png?access-token=1HxubgB7ToJiUX3kEi7hGfaFJoxPpDwExwEifjbBjcOXE7m0mLsvxzA7McLVTRbf',
        attr="Tiles Courtesy of Jawg Maps")

    if (bounds is None):
        sw = df[['latitude', 'longitude']].min().values.tolist()
        ne = df[['latitude', 'longitude']].max().values.tolist()
        bounds = [sw, ne]

    base_map.fit_bounds(bounds)
    main_uid = user_row['business_id']
    for i in range(0, len(df)):
        if df.iloc[i]['business_id'] != main_uid:
            popup_content = get_popup_content(main_uid, df.iloc[i], df, df_reviews=df_reviews)
            folium.Marker(
                location=[df.iloc[i]['latitude'], df.iloc[i]['longitude']],
                tooltip="<b>" + df.iloc[i]['name'] + "</b>",
                popup=popup_content
            ).add_to(base_map)

    popup_content = get_popup_content(main_uid, user_row, df, mine=True)
    folium.Marker(
        location=[user_row['latitude'], user_row['longitude']],
        tooltip="<b>" + user_row['name'] + "</b>",
        popup=popup_content,
        icon=folium.Icon(color="red")
    ).add_to(base_map)

    return base_map


def get_popup_content(main_uid, row, df, mine=False, df_reviews=None):
    if (mine):
        content = "<h2>Your Restaurant!</h2>"
    else:
        content = ""

    content = content + "<h3>" + str(row["name"]) + ", " + str(row["city"]) + ", " + str(
        row["state"]) + "</h3><hr><h4>" + str(row["categories"]) + "</h4>Average Stars: " + str(row["stars"])

    content = content + "<br><br>Top Review: " + str(row["text"])

    if (mine == False):
        exclusive_attrs = get_exclusive_attrs(main_uid, row['business_id'], df)
        if (len(exclusive_attrs) > 0):
            content = content + "<br><br>Attributes of this business that are missing in your business:<br><ul>"
            for ea in exclusive_attrs:
                content = content + "<li>" + str(ea) + "</li>"
            content = content + "</ul>"

        content = content + "<br><br><button onclick='myFunction()'>View Detailed Comparison</button><br><br>"
        content = content + """<script>
                                        function myFunction() {
                                            var x = document.getElementById("vis");
                                            if (x.style.display === "none") {
                                            x.style.display = "block";
                                            } else {
                                            x.style.display = "none";
                                            }
                                        }
                                    </script>"""

        vis = compare_businesses(df_reviews, df, main_uid, row['business_id'])
        a = vis.to_html()
        a = a.replace('<div id="vis">', '<div id="vis" style="display:none">')
        content = a.replace('<body>', '<body>' + content)

    iframe = folium.IFrame(content, width=550, height=400)
    popup = folium.Popup(iframe)
    return popup


def generate_map_vis(business_id, df_reviews):

    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        st.markdown(
            "<p> <span class='material-icons'> storefront </span>Use the visualization below to study restaurants in "
            "your area that are either similar to yours, "
            "or filter based on features of a business. Similarity scores are calculated based on the cosine "
            "similarity between attributes of you restaurant and every other restaurant in your state. Hover over a "
            "pin to get comparitive information about the restaurant and  and unlock more comparitive "
            "visualizations</p>",
            unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 7, 1])
    with col2:
        with st.spinner(text="Loading data..."):
            busi = load_data()

        user_row_raw = busi[busi['business_id'] == business_id]
        user_row = user_row_raw.iloc[0]
        filter_option = st.radio("Compare To: ", ["Similar Businesses in State", "Businesses in the Same City"], index=1)

        if (filter_option == "Similar Businesses in State"):
            df = similarity(business_id, busi, 50)

        else:
            CITY = user_row["city"]
            df = busi[busi["city"] == CITY][:50]

        df_cat = df[['business_id', 'categories']]
        df_cat['categories'] = df_cat['categories'].str.split(",")
        df_cat = df_cat.explode('categories')
        df_cat = df_cat[df_cat["categories"] != "Restaurants"]

        selected_category = st.multiselect("Category", df_cat['categories'].unique())
        selected_rating = st.slider("Average Rating", 0, 5, (1, 4))

        filters = get_filtered_rows(df, df_cat, selected_category, selected_rating, business_id)
        filters = df[filters]

        if len(filters) == 0 or business_id not in filters['business_id'].to_list():
            filters = pd.concat([user_row_raw, filters])

        with st.spinner(text="Filtering Restaurant"):
            sw = df[['latitude', 'longitude']].min().values.tolist()
            ne = df[['latitude', 'longitude']].max().values.tolist()
            bounds = [sw, ne]
            base_map = plot_map(user_row, filters, df_reviews, bounds=bounds)
            folium_static(base_map)
