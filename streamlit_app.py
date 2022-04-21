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
for i in range(len(list_of_attributes)):
    text = list_of_attributes[i].split('.')[1]
    parameter_name_lookup[text] = list_of_attributes[i]
feature_selectbox = st.selectbox("Select visualisation paramter", parameter_name_lookup.keys())

#storm_data = visualise_storm(name_selectbox, year_selectbox)
new_data = data[['stars', parameter_name_lookup[feature_selectbox]]].dropna()
new_data = new_data.groupby(['stars'])
print(new_data)
progression_chart = alt.Chart(new_data).mark_line().encode(
    y = 'stars',
    x = parameter_name_lookup[feature_selectbox]
)
st.write(progression_chart)