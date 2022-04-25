from tkinter import Y
import streamlit as st
import pandas as pd
import altair as alt

class overallVis:
    def __init__(self):
        self.df =  pd.read_csv('data/preprocess_business.csv', dtype=str)
        self.df = self.df.drop(columns = ['Unnamed: 0'])
        #d = {'true': True, 'false': False}
        #c = {1: True, 0: False}
        #e = {"u'free'" : "'free'", "u'no'" : "'no'", "u'paid'" : "'paid'"}
        #self.df = self.df.replace(d)
        #self.df = self.df.replace(c)
        #self.df = self.df.replace(e)
    
    def vis_draw(self):
        return self.df.head()

    def overall_bar(self):
        data = self.df
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
        state_selectbox = st.multiselect("Select states to narrow your search area", data['state'].unique())
        if len(state_selectbox) != 0:
            data = data[data['state'].isin(state_selectbox)]
        city_selectbox = st.multiselect("Select city to narrow your search area", data['city'].unique())
        if len(city_selectbox) != 0:
            data = data[data['city'].isin(city_selectbox)]
        if data.empty:
            st.write('The selections made for City and State don\'t having any ratings data available, please reselect the values that have more than 1 value, Thank You')
        else:
            feature_selectbox = st.multiselect("Select visualisation paramter", parameter_name_lookup.keys(), default='WiFi')
            data.rename(columns=rename, inplace=True)
            attributes = ['stars'] + feature_selectbox
            new_data = data[attributes]
            for i in range(len(feature_selectbox)):
                df = new_data#[new_data[feature_selectbox[i] == None]]
                progression_chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X(feature_selectbox[i], axis=alt.Axis(title=feature_selectbox[i], titleOpacity=0)),
                    y=alt.Y('count():Q', axis=alt.Axis(title='Count')),
                    column=alt.Column('stars', title='Star Ratings'),
                    color=alt.Color(feature_selectbox[i]),
                    tooltip=['count()']
                ).properties(
                width=50,
                height=600,
                title='Star Ratings vs Attributes'
                ).configure_view(
                    strokeWidth=0, width = 0
                )
                st.write(progression_chart)


    def overall_view(self):
        data = self.df
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
        new_data = data[['stars', feature_selectbox]]

        d = pd.crosstab(new_data[feature_selectbox], columns=new_data.stars)
        d = d.stack().reset_index()
        d = d.rename(columns={0:'CummulativeCount'})
        legend_selection = alt.selection_multi(fields=[feature_selectbox], bind='legend')
        lines = alt.Chart(d).mark_line().encode(
            x=alt.X('stars', axis=alt.Axis(title='Star Ratings')),
            y=alt.Y('CummulativeCount', axis=alt.Axis(title='Count')),
            color=alt.Color(feature_selectbox, legend=alt.Legend(title=feature_selectbox)),
            opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.1)),
        ).properties(
        width=1200,
        height=600,
        title='Star Ratings vs ' + feature_selectbox
        )
        nearest_selector = alt.selection(type='single', nearest=True, on='mouseover',
                                        fields=['stars'], empty='none')

        selectors = alt.Chart(d).mark_point().encode(
            x='stars',
            opacity=alt.value(0),
        ).add_selection(nearest_selector)

        points = lines.mark_point().encode(
            opacity=alt.condition(nearest_selector, alt.value(1), alt.value(0))
        )

        text = lines.mark_text(align='left', dx=5, dy=-5).encode(
            text=alt.condition(nearest_selector, 'CummulativeCount:Q', alt.value(' '))
        )

        rules = alt.Chart(d).mark_rule(color='gray').encode(
            x='stars',
        ).transform_filter(nearest_selector)

        layered_chart = alt.layer(
            lines, selectors, points, rules, text
        ).add_selection(
            legend_selection
        ).properties(
            width=800, height=400
        )
        st.write(layered_chart)

