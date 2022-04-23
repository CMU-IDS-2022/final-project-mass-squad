from markdown import markdown
from numpy import int32
import streamlit as st
import pandas as pd
import altair as alt
from wordcloud import WordCloud
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from sklearn.feature_extraction._stop_words import ENGLISH_STOP_WORDS

from OverallView import overallVis


st.set_page_config(layout="wide")

st.markdown(
    """<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    """,
    unsafe_allow_html=True)

st.sidebar.image("yelp-logo-vector.png", use_column_width=True, output_format="PNG")

#import nltk
#nltk.download('stopwords')
@st.cache
def read_data():
    merged_df = pd.read_csv('data/merged_reviews.csv')
    return merged_df

merged_df = read_data()
obj = overallVis()

def welcome_page():
    if st.checkbox("Show Cleaned Data"):
        st.write("Cleaning involved splitting data by spaces, combining entires like 'tropical datastorm' that got split redundantly, formatting strings with extra quotes, and for pressure as the storm becomes a Hurricane the pressure drops to lowest possible levels thus we have filled the NaN with 0")
        st.write(merged_df)
        st.write(obj.df)

def overall_view():
    
    st.title("Yelp Restaraunt Analysis")

    data = obj.df
    all_keys = data.keys().to_list()
    list_of_attributes = []
    for i in range(len(all_keys)):
        if 'attributes' in all_keys[i]:
            list_of_attributes.append(all_keys[i])

    parameter_name_lookup = dict()
    rename = dict()
    for i in range(len(list_of_attributes)):
        text = list_of_attributes[i].split('.')[1]
        parameter_name_lookup[text] = list_of_attributes[i]
        rename[list_of_attributes[i]] = text
    feature_selectbox = st.selectbox("Select visualisation paramter", parameter_name_lookup.keys())
    data.rename(columns=rename, inplace=True)
    new_data = data[['stars', feature_selectbox]].dropna()

    d = pd.crosstab(new_data[feature_selectbox], columns=new_data.stars)
    d = d.stack().reset_index()
    d = d.rename(columns={0:'CummulativeCount'})
    progression_chart = alt.Chart(d).mark_line().encode(
        x = alt.X('stars', axis=alt.Axis(title='Star Ratings')),
        y=alt.Y('CummulativeCount', axis=alt.Axis(title='Count')),
        color=alt.Color(feature_selectbox, legend=alt.Legend(title=feature_selectbox))
    ).properties(
    width=1200,
    height=600,
    title='Star Ratings vs ' + feature_selectbox
    )
    st.write(progression_chart)


def specific_restaraunt():
    all_business_ids = merged_df['name'].unique().tolist()

    '''
    ## Analyse your business with visualizations!
    '''
    feature_selectbox = st.selectbox("Select your business_id", all_business_ids)

    # TODO: change to dynamic
    my_business_df = merged_df[merged_df['name'] == "Matt's Big Breakfast"]
    #print(my_business_df['name'])


    ## WORDCLOUD
    stopword_set = set(stopwords.words('english') + list(ENGLISH_STOP_WORDS))
    full_text = ' '.join(my_business_df['text'].dropna())
    cloud_no_stopword = WordCloud(background_color='white', stopwords=stopword_set, width=800, height=400, repeat=True).generate(full_text)
    plt.imshow(cloud_no_stopword, interpolation='bilinear')
    plt.axis('off')
    #plt.show()
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()


    '''
    ## STAR DISTRIBUTION
    '''
    df = pd.DataFrame(my_business_df['stars_review'].value_counts(), columns=['stars_review'])
    st.dataframe(my_business_df['stars_review'].value_counts())
    distribution_df = my_business_df['stars_review'].value_counts().reset_index()

    distribution_chart = alt.Chart(distribution_df).mark_bar().encode(
    y=alt.Y('stars_review', title="Rating Count"),
    x=alt.X('index:N', title = "Star-rating"),
    ).properties(
        title="Star Rating Distribution",
        width=600

    ).interactive()
    st.altair_chart(distribution_chart)

    '''
    ## RATING OVER TIME
    '''
    my_business_df['date'] = pd.to_datetime(my_business_df['date'])
    date_df = my_business_df.groupby(my_business_df.date.dt.year).mean()
    st.dataframe(date_df['stars_review'])
    date_df = date_df.reset_index()
    #st.line_chart(date_df['stars_review'])

    ratings_chart = alt.Chart(date_df).mark_line().encode(
    x=alt.X('date:T', title="Year"),
    y=alt.Y('stars_review:Q', title = "Average Star rating from Reviews"),
    tooltip = ['stars_review']
    ).properties(
        title="Average Star Ratings over Time"
    ).interactive()
    st.altair_chart(ratings_chart)


def display_graph(selection="Hello"):
    if "menu" in st.session_state:
        selection = st.session_state.menu
    if selection == 'Overall Landscape':
        overall_view()
    elif selection == "Your Restaraunt":
        specific_restaraunt()
    elif selection == "Similarity Check":
        #AllForNow()
        st.markdown('hello my good friend')
    else:
        welcome_page()

st.session_state.mask = 'Hello'

selector = st.sidebar.selectbox(
    "Yelp Restaraunt Analysis",
    ("Select One", "Overall Landscape", "Your Restaraunt", "Similarity Check"),
    on_change=display_graph(),
    key="menu",
)

#  ------------------- Top Bar details here ----------------------



