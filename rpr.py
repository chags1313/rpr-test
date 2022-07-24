# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Thu May 19 15:15:40 2022

@author: chags
"""


# -*- coding: utf-8 -*-
"""
Created on Sat Jul 23 21:39:13 2022

@author: chags
"""

# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Thu May 19 15:15:40 2022

@author: chags
"""


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
filen = 0
com = pd.DataFrame()
multiple_files = st.file_uploader(
    "Multiple File Uploader",
    accept_multiple_files=True
)
for file in multiple_files:
    file_container = st.beta_expander(
        f"File name: {file.name} ({file.size})")
    data = StringIO.BytesIO(file.getbuffer())
    file_container.write(pd.read_csv(data))

st.write("### Code")
uploaded_file = st.sidebar.file_uploader("Upload Your RPR Test File", accept_multiple_files=True)
filen = 50
if uploaded_file is not None:
            filen = + 1
            # To read file as bytes:
            for file in uploaded_file:
            #st.write(bytes_data)

             # To convert to a string based IO:
                 data = StringIO.BytesIO(file.getbuffer())

                 dataframe = pd.read_csv(data)
            dataframe['Date and Time of Test'] = str(dataframe['Datetime'].iloc[0])
            st.write(dataframe)
            com = dataframe
            #com = pd.concat([dataframe, com], axis=0, join='inner')
            rrfdate = px.box(com, x= 'Datetime', y = 'Relative Resistance to Flow', color_discrete_sequence=['purple'])
            st.plotly_chart(rrfdate)
            sheardate = px.box(com, x= 'Datetime', y = 'Shear Rate', color_discrete_sequence=['green'])
            st.plotly_chart(sheardate)
            com['Flow Time in Seconds'] = com['Blood Sample']
            comp = px.scatter(com, x='mmHg range', y = 'Flow Time', color = 'Date and Time of Test')
            st.plotly_chart(comp)
                        
