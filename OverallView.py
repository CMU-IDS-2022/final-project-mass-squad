import streamlit as st
import pandas as pd
import altair as alt

class overallVis:
    def __init__(self):
        self.df =  pd.read_csv('data/preprocessed_business.csv', dtype=str)
        self.df = self.df.drop(columns = ['Unnamed: 0', 'attributes.WiFi'])
        #d = {'true': True, 'false': False}
        #c = {1: True, 0: False}
        #e = {"u'free'" : "'free'", "u'no'" : "'no'", "u'paid'" : "'paid'"}
        #self.df = self.df.replace(d)
        #self.df = self.df.replace(c)
        #self.df = self.df.replace(e)
    
    def vis_draw(self):
        return self.df.head()
