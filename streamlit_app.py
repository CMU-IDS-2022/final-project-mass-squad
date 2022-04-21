from numpy import int32
import streamlit as st
import pandas as pd
import altair as alt

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