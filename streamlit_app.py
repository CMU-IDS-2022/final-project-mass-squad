from markdown import markdown
from numpy import int32
import streamlit as st
import pandas as pd
import altair as alt
from wordcloud import WordCloud


st.set_page_config(layout="wide")

st.markdown(
    """<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    """,
    unsafe_allow_html=True)

#st.sidebar.image("img/proto.png", use_column_width=True, output_format="PNG")

#import nltk
#nltk.download('stopwords')
def AllForNow():
    from nltk.corpus import stopwords
    import matplotlib.pyplot as plt
    from sklearn.feature_extraction._stop_words import ENGLISH_STOP_WORDS

    from OverallView import overallVis
    st.title("Yelp Restaraunt Analysis")
    obj = overallVis()

    data = obj.df
    all_keys = data.keys().to_list()
    list_of_attributes = []
    for i in range(len(all_keys)):
        if 'attributes' in all_keys[i]:
            list_of_attributes.append(all_keys[i])

    st.write(data)

    parameter_name_lookup = dict()
    rename = dict()
    for i in range(len(list_of_attributes)):
        text = list_of_attributes[i].split('.')[1]
        parameter_name_lookup[text] = list_of_attributes[i]
        rename[list_of_attributes[i]] = text
    feature_selectbox = st.selectbox("Select visualisation paramter", parameter_name_lookup.keys())
    data.rename(columns=rename, inplace=True)
    #storm_data = visualise_storm(name_selectbox, year_selectbox)
    new_data = data[['stars', feature_selectbox]].dropna()
    #new_data = new_data.groupby(['stars']).count()
    #new_data = new_data.pivot_table('stars', parameter_name_lookup[feature_selectbox], aggfunc='count').reset_index()
    #print(new_data)
    #print(data[list_of_attributes].mean())
    #d = pd.crosstab(new_data.stars, columns=new_data[parameter_name_lookup[feature_selectbox]]).cumsum()

    d = pd.crosstab(new_data[feature_selectbox], columns=new_data.stars)
    d = d.stack().reset_index()
    d = d.rename(columns={0:'CummulativeCount'})
    progression_chart = alt.Chart(d).mark_line().encode(
        x = 'stars',
        y='CummulativeCount',
        color=feature_selectbox+':N'
    )
    st.write(progression_chart)


    @st.cache
    def read_data():
        merged_df = pd.read_csv('data/merged_reviews.csv')
        return merged_df

    merged_df = read_data()
    all_business_ids = merged_df['name'].unique().tolist()

    st.dataframe(merged_df)
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
    st.bar_chart(df)

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
    )
    st.altair_chart(ratings_chart)


def display_graph(selection="Hello"):
    if "menu" in st.session_state:
        selection = st.session_state.menu
    if selection == 'Overall Landscape':
        st.markdown('stuff')
    elif selection == "Your Restaraunt":
        AllForNow()
    elif selection == "Similarity Check":
        AllForNow()

st.session_state.mask = 'Hello'

selector = st.sidebar.selectbox(
    "Yelp Restaraunt Analysis",
    ("Select One", "Overall Landscape", "Your Restaraunt", "Similarity Check"),
    on_change=display_graph(),
    key="menu",
)

#  ------------------- Top Bar details here ----------------------



