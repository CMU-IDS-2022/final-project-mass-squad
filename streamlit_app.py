import streamlit as st
import pandas as pd
import altair as alt
from OverallView import overallVis
st.title("Yelp Restaraunt Analysis")
obj = overallVis()
st.write(obj.df)