from markdown import markdown
from numpy import int32
import streamlit as st
import pandas as pd
import altair as alt
from wordcloud import WordCloud
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from sklearn.feature_extraction._stop_words import ENGLISH_STOP_WORDS
import folium
from streamlit_folium import folium_static


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

@st.cache
def load_data():
    """
    Write 1-2 lines of code here to load the data from CSV to a pandas dataframe
    and return it.
    """
    busi = pd.read_csv("data/processed_business_anj.csv")
    busi['name'] = busi['name'].str.replace('"','')
    return busi

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

def get_popup_content(row): 
    content = "<h3>"+row["name"]+", "+row["city"]+", "+row["state"]+"</h3><hr>Neighborhood: "+row["neighborhood"]+"<br>Address: "+row["address"]+"<br>Average Stars: "+str(row["stars"])
    iframe = folium.IFrame(content, width=275, height=150)
    popup = folium.Popup(iframe)
    return popup
  

def generate_map_vis(CITY = "Westmount"):
    st.title("Map Plot of Yelp Restaurants")
    with st.spinner(text="Loading data..."):
        busi = load_data()

    df = busi[busi["city"]==CITY]
    df_cat = df[['business_id','categories']]
    df_cat['categories'] = df_cat['categories'].str.split(";")
    df_cat = df_cat.explode('categories')
    df_cat = df_cat[df_cat["categories"]!="Restaurants"]

    selected_category = st.multiselect("Category", df_cat['categories'].unique())
    selected_rating = st.slider("Average Rating",0,5,(1,4))

    filters = get_filtered_rows(df, df_cat, selected_category, selected_rating)
    filters = df[filters]

    with st.spinner(text="Filtering Restaurants"):
        base_map = folium.Map(
        location=[45.4784, -73.6028],height='100%', width = '100%',
        tiles='https://{s}.tile.jawg.io/jawg-streets/{z}/{x}/{y}{r}.png?access-token=1HxubgB7ToJiUX3kEi7hGfaFJoxPpDwExwEifjbBjcOXE7m0mLsvxzA7McLVTRbf',
        attr="Tiles Courtesy of Jawg Maps")

        sw = df[['latitude', 'longitude']].min().values.tolist()
        ne = df[['latitude', 'longitude']].max().values.tolist()

        base_map.fit_bounds([sw, ne]) 

        for i in range(0,len(filters)):
            popup_content = get_popup_content(filters.iloc[i])   
            folium.Marker(
                location=[filters.iloc[i]['latitude'], filters.iloc[i]['longitude']],
                tooltip="<b>"+filters.iloc[i]['name']+"</b>",
                popup= popup_content
            ).add_to(base_map)
        
        folium_static(base_map)


merged_df = read_data()
obj = overallVis()

def welcome_page():
    if st.checkbox("Show Cleaned Data"):
        st.write("Cleaning involved splitting data by spaces, combining entires like 'tropical datastorm' that got split redundantly, formatting strings with extra quotes, and for pressure as the storm becomes a Hurricane the pressure drops to lowest possible levels thus we have filled the NaN with 0")
        st.write(merged_df)
        st.write(obj.df)


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
    if st.checkbox("Show Star Rating Count"):
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
    if st.checkbox("Show Year-wise Average Star Rating"):
        st.dataframe(date_df['stars_review'])
    date_df = date_df.reset_index()
    #st.line_chart(date_df['stars_review'])

    ratings_chart = alt.Chart(date_df).encode(
        x=alt.X('date:T', title="Year"),
        y=alt.Y('stars_review:Q', title = "Average Star rating from Reviews"),
        tooltip = ['stars_review']
    ).properties(
        title="Average Star Ratings over Time"
    )
    st.altair_chart((ratings_chart.mark_line() + ratings_chart.mark_point(filled=True, size=40)).interactive())



def display_graph(selection="Hello"):
    if "menu" in st.session_state:
        selection = st.session_state.menu
    if selection == 'Overall Landscape':
        st.title("Overall Landscape of restaraunts")
        obj.overall_view()
    elif selection == "Your Restaraunt":
        specific_restaraunt()
    elif selection == "Similarity Check":
        generate_map_vis() 
    else:
        st.title('Hello their welcome to our webpage')
        welcome_page()

st.session_state.mask = 'Hello'

selector = st.sidebar.selectbox(
    "Yelp Restaraunt Analysis",
    ("Select One", "Overall Landscape", "Your Restaraunt", "Similarity Check"),
    on_change=display_graph(),
    key="menu",
)

#  ------------------- Top Bar details here ----------------------



