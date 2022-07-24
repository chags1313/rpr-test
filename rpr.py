
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


#st.title("RPR Analysis")
st.sidebar.title("Rapid Profile Rheometer 🩸")

uploaded_file = st.sidebar.file_uploader("Upload Your RPR Test File", type="csv", accept_multiple_files=True)
if uploaded_file is not None:
            # To read file as bytes:
            for file in uploaded_file:

                 dataframe = pd.read_csv(uploaded_file)
                 file.seek(0)
            dataframe['Date and Time of Test'] = str(dataframe['Datetime'].iloc[0])
            st.write(dataframe)

            com = pd.concat([dataframe, com], axis=0, join='inner')
            rrfdate = px.box(com, x= 'Datetime', y = 'Relative Resistance to Flow', color_discrete_sequence=['purple'])
            st.plotly_chart(rrfdate)
            sheardate = px.box(com, x= 'Datetime', y = 'Shear Rate', color_discrete_sequence=['green'])
            st.plotly_chart(sheardate)
            com['Flow Time in Seconds'] = com['Blood Sample']
            comp = px.scatter(com, x='mmHg range', y = 'Flow Time', color = 'Date and Time of Test')
            st.plotly_chart(comp)
                        
