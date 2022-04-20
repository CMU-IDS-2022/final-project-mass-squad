import streamlit as st
import pandas as pd
import altair as alt

class overallVis:
    def __init__(self):
        self.df =  pd.read_csv('/home/sidharth/Documents/2022/Spring-2022/IDS/final-project-mass-squad/data/processed_business.csv')
        self.df = self.df.drop(columns = 'Unnamed: 0')
    
    def vis_draw(self):
        return self.df.head()