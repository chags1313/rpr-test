


import streamlit as st
from io import StringIO
import pandas as pd
import plotly.express as px
import numpy as np


st.set_page_config(layout="wide")
pd.set_option('max_colwidth', 400)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
filen = 0

#st.title("RPR Analysis")
st.sidebar.title("Rapid Profile Rheometer 🩸 Compare Tool")
com = pd.DataFrame()
com1 = pd.DataFrame()
com1['Datetime'] = 'na'
com1['Relative Resistance to Flow'] = 'na'
com1['Shear Rate'] = 'na'
com1['Flow Time in Seconds'] = 'na'
com1['mmHg range'] = 'na'
com1['Blood Sample'] = 'na'
com1['Date and Time of Test'] = 'na'

dataframe = pd.DataFrame()

uploaded_file = st.sidebar.file_uploader("Upload RPR Analytics Files", type="csv", accept_multiple_files=True)
if uploaded_file is not None:
    
            # To read file as bytes:
            for file in uploaded_file:
                 dataframe = pd.read_csv(file)
                 dataframe['Date and Time of Test'] = str(dataframe['Datetime'].iloc[0])
                 file.seek(0)
                 com1 = pd.concat([com1, dataframe])

            rrfdate = px.box(com1, x= 'Date and Time of Test', y = 'Relative Resistance to Flow', color_discrete_sequence=['purple'])
            #rrfdate.update_layout()
            rrfdate.update_xaxes(type='category')
            st.plotly_chart(rrfdate,config= dict(
            displayModeBar = False))
            sheardate = px.box(com1, x= 'Date and Time of Test', y = 'Shear Rate', color_discrete_sequence=['green'])
            #sheardate.update_layout()
            sheardate.update_xaxes(type='category')
            st.plotly_chart(sheardate,config= dict(
            displayModeBar = False))
            com1['Flow Time in Seconds'] = com1['Blood Sample']
            comp = px.scatter(com1, x='mmHg range', y = 'Flow Time in Seconds', color = 'Date and Time of Test', color_continuous_scale=px.colors.sequential)
            comp.update_layout(width = 820)
            st.plotly_chart(comp,config= dict(
            displayModeBar = False))
            
