# -*- coding: utf-8 -*-
"""
Created on Thu May 19 15:15:40 2022

@author: chags
"""

import streamlit as st
#import StringIO
from io import StringIO
import pandas as pd
import plotly.express as px

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

#st.title("RPR Analysis")
st.sidebar.title("Rapid Profile Rheometer 🩸")
pages = st.sidebar.selectbox("Pages", ['Analytics'])


    

if pages == 'Analytics':

    uploaded_file = st.sidebar.file_uploader("Upload Your RPR Test File")

    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
            #st.write(bytes_data)

         # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
             #st.write(stringio)

         # To read file as string:
        string_data = stringio.read()
     #st.write(string_data)

     # Can be used wherever a "file-like" object is accepted:
        dataframe = pd.read_csv(uploaded_file)
        dataframe['Seconds'] = dataframe.index / 1000
    #st.sidebar.dataframe(dataframe)
     #fig = px.scatter(dataframe,  y="Amplitude - Normalized Pressure Data", x = 'Seconds')
     #st.plotly_chart(fig)
        wad = dataframe
        wadmax = wad['Amplitude - Normalized Pressure Data'].idxmax()
        wadmin = wad['Amplitude - Normalized Pressure Data'].idxmin()
        fir_curve = wad['Amplitude - Normalized Pressure Data'].iloc[wadmax:wadmin-200]
        sec_curve = wad['Amplitude - Normalized Pressure Data'].iloc[wadmin:]
        R = ((0.0165 * 2.54) / 100)
        pi = 3.14256
        first = fir_curve.iloc[20]
        last = fir_curve.iloc[-1]
        curve =  first - last
        maximum = fir_curve.max()
        time = len(fir_curve) / 1000
        Q = ((((0.6 * curve) / 20 / time)) * (1*10**-6))


        shear = 4*(Q/(pi*(R**3)))
        fir_curve1 = pd.DataFrame(fir_curve)
        fir_curve1['shear'] = 'na'
        with st.spinner("Proccessing Analytics"):
             for i in range(len(fir_curve1)):
                 first = fir_curve1['Amplitude - Normalized Pressure Data'].iloc[i] 
                 last = fir_curve1['Amplitude - Normalized Pressure Data'].iloc[-1] 
                 curve =  first - last
                 Q = ((((0.6 * curve) / 15) / time)) * (1*10**-6)
                 shear = 4*(Q/(pi*(R**3)))
                 print(shear)
                 fir_curve1['shear'].iloc[i] = shear

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label = 'Time of Flow in Seconds', value = time)
        with col2:
            st.metric(label = "Maximum Presuure mmHg", value = max(fir_curve))
        with col3:
            st.metric(label= "Average Shear Rate", value = int(fir_curve1['shear'].mean()))
        wad['First Curve'] = (wad.index.isin(fir_curve.index)).astype(int)
        wad['Second Curve'] = (wad.index.isin(sec_curve.index)).astype(int)
        wad['curves'] = wad['First Curve'] + wad['Second Curve']
        wad['curves'] = wad['curves'].replace(0, "No Identified Curve")
        wad['curves'] = wad['curves'].replace(1, "Curve Used For Analysis")
        avg_curve = (fir_curve + sec_curve[:len(fir_curve)].abs()) / 2
     
        st.header("Test Results - Curves Selected for Analysis")
        fig =  px.scatter(wad, y='Amplitude - Normalized Pressure Data',x= "Seconds", color = 'curves',color_discrete_sequence=["gray", "red"])
        st.plotly_chart(fig)

        st.header("Shear Rate by Pressure")      
        shearfig = px.scatter(fir_curve1, y='shear', x='Amplitude - Normalized Pressure Data',color_discrete_sequence=["black"])
        st.plotly_chart(shearfig)
        st.header('Averaged Curve Data')
        with st.expander("Data"):
            st.dataframe(fir_curve1)
        @st.cache
        def convert_df(df):
         # IMPORTANT: Cache the conversion to prevent computation on every rerun
             return df.to_csv().encode('utf-8')

        csv = convert_df(fir_curve1)

        st.sidebar.download_button(
             label="Download data as CSV",
             data=csv,
             file_name='Results.csv',
             mime='text/csv',
             )

    