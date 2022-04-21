import streamlit as st
import pandas as pd
import altair as alt

class overallVis:
    def __init__(self):
        self.df =  pd.read_csv('/home/sidharth/Documents/2022/Spring-2022/IDS/final-project-mass-squad/data/processed_business_attributes.csv', dtype=str)
        self.df = self.df.drop(columns = ['Unnamed: 0', 'hours', 'attributes'])
        #d = {'true': True, 'false': False}
        #c = {1: True, 0: False}
        e = {"u'free'" : "'free'", "u'no'" : "'no'", "u'paid'" : "'paid'"}
        #self.df = self.df.replace(d)
        #self.df = self.df.replace(c)
        self.df = self.df.replace(e)
    
    def vis_draw(self):
        return self.df.head()