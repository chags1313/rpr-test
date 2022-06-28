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
pages = st.sidebar.selectbox("Pages", ['Analytics', "Test Results"])

    

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
        avg_curve = (fir_curve.reset_index(drop=True) + sec_curve[:len(fir_curve)].reset_index(drop=True).abs()) / 2
        avg_curve1 = pd.DataFrame()
        avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve
        last_point = avg_curve1['Amplitude - Normalized Pressure Data'].iloc[-1]
        avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve1['Amplitude - Normalized Pressure Data'] -  1.1
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
        avg_curve1['shear'] = 'na'
        avg_curve1['flow'] = 'na'
        with st.spinner("Proccessing Analytics"):
             for i in range(len(avg_curve1)):
                 first = avg_curve1['Amplitude - Normalized Pressure Data'].iloc[i] 
                 last = avg_curve1['Amplitude - Normalized Pressure Data'].iloc[-1] 
                 curve =  first - last
                 Q = ((((0.6 * curve) / 15) / time)) * (1*10**-6)
                 shear = 4*(Q/(pi*(R**3)))
                 print(shear)
                 avg_curve1['shear'].iloc[i] = shear
                 avg_curve1['flow'].iloc[i] = Q

        wad['First Curve'] = (wad.index.isin(fir_curve.index)).astype(int)
        wad['Second Curve'] = (wad.index.isin(sec_curve.index)).astype(int)
        wad['curves'] = wad['First Curve'] + wad['Second Curve']
        wad['curves'] = wad['curves'].replace(0, "No Identified Curve")
        wad['curves'] = wad['curves'].replace(1, "Curve Used For Analysis")
        avg_curve = (fir_curve.reset_index(drop=True) + sec_curve[:len(fir_curve)].reset_index(drop=True).abs()) / 2
        cur = pd.DataFrame()
        cur['First Curve'] = fir_curve.reset_index(drop=True)
        cur['Second Curve'] = sec_curve[:len(fir_curve)].abs().reset_index(drop=True)
        cur["Averaged Curve"] = avg_curve
        cur['Time'] = cur.index / 1000
        cur['Shear Rate'] = avg_curve1['shear']
        cur['Flow'] = avg_curve1['flow']
        df_melt = cur.melt(id_vars="Time", value_vars=['First Curve', 'Second Curve', 'Averaged Curve'])
        water = [0.038333333,
0.0335,
0.033,
0.034666667,
0.05,
0.0395,
0.042333333,
0.040666667,
0.045333333,
0.047333333,
0.056666667,
0.0545,
0.061166667,
0.071333333,
0.071833333,
0.094333333,
0.100333333,
0.1835,
0.185,
0.187
]

        bld = list()
        num = list()
        shr = list()
        last_point = cur['Averaged Curve'].iloc[-1]
        cur['Averaged Curve'] = cur['Averaged Curve'] -  1.1
        for numbers in reversed(np.arange(0.5, 10.5, 0.5)):
            #bld.append(len(cur[cur['Averaged Curve'] < numbers]) / 1000)
            u = cur[cur['Averaged Curve'] < numbers]
            z = cur[cur['Averaged Curve'] < numbers - 0.5]
            bld.append((len(u) - len(z))/ 1000) 
            num.append(numbers)
        for numbers in reversed(np.arange(0.5, 10.5, 0.5)):
            z = avg_curve1[avg_curve1['Amplitude - Normalized Pressure Data'] < numbers]
            shr.append((z['shear'].max()))
        rrf = pd.DataFrame({'Water Control': water})
        rrf['Blood Sample'] = bld
        rrf['Relative Resistance to Flow'] = 'na'
        rrf['mmHg range'] = 'na'
        rrf['mmHg'] = num
        rrf['Shear Rate'] = shr
        for i in range(len(rrf)):
            rrf['Relative Resistance to Flow'].iloc[i] = rrf['Blood Sample'].iloc[i] / rrf['Water Control'].iloc[i]
            high = rrf['mmHg'].iloc[i]
            low = rrf['mmHg'].iloc[i] - 0.5
            rrf['mmHg range'].iloc[i] = str(high) + " to " + str(low)
       
        c1, c2, c3 = st.columns(3)
        with c3:
            st.text("Sample Flow Time")
            st.info(str(round(time, 2)) + " s")
        with c2:
            st.text("Sample Validity")
            st.info("0.97")
        with c1:
            st.text("Mean RRF")
            meann = rrf['Relative Resistance to Flow'].median()
            st.success(str(round(meann, 2)))
            
        e1, e2 = st.columns(2)
     
        
        fig =  px.scatter(wad, y='Amplitude - Normalized Pressure Data',x= "Seconds", color = 'curves',color_discrete_sequence=["gray", "red"])
        
        
        cur['flow'] = cur['Flow'].rolling(window= 1000).mean().diff()
        cur['shear rate'] = cur['Shear Rate'].rolling(window=1000).mean()
        cur['Average curve mmHg'] = cur['Averaged Curve'].rolling(window=100).mean()
        #cur[(np.abs(stats.zscore(cur["Shear Rate"])) < 2)]
        
        avg_plt = px.line(cur, x= 'Time',y = "Average curve mmHg", color_discrete_sequence=['black'])
        
        shears = px.scatter(rrf, x='Shear Rate', y='Relative Resistance to Flow', color_discrete_sequence=['orange'], trendline="lowess")
        with e1:
            st.plotly_chart(shears)
             
             
        shears1 = px.scatter(rrf,x = 'mmHg',  y=['Blood Sample', 'Water Control'], color_discrete_sequence=['red', 'blue'], trendline='lowess')
        shears1.update_layout(yaxis_title="Time of Flow in Seconds")
        with e2:
            st.plotly_chart(shears1)
        xx1, xx2 = st.columns(2)
        with xx1:
            st.dataframe(rrf[['Shear Rate','Relative Resistance to Flow', 'mmHg range']].style.background_gradient(cmap='Greens', subset=['Shear Rate','Relative Resistance to Flow']).set_properties(subset=['Shear Rate','Relative Resistance to Flow', 'mmHg range'], **{'width': '300px'}), height=1000, width=800)

        @st.cache
        def convert_df(df):
         # IMPORTANT: Cache the conversion to prevent computation on every rerun
             return df.to_csv().encode('utf-8')

        csv = convert_df(rrf)
        with xx2:
            st.text("High Shear Rate")
            hsr = max(rrf['Shear Rate'])
            st.warning(str(round(hsr, 2)) + " -s")
            st.text("Low Relative Resistance to Flow")
            hi = min(rrf['Relative Resistance to Flow'])
            st.warning(str(round(hi, 2)))
            st.text("Low Shear Rate")
            lsr = min(rrf['Shear Rate'])
            st.error(str(round(lsr, 2)) + " -s")
            st.text("High Relative Resistance to Flow")
            lo = max(rrf['Relative Resistance to Flow'])
            st.error(str(round(lo, 2)))
            


            
            
            st.text("Save All Data")
            st.download_button(
             label="Download data as CSV",
             data=csv,
             file_name='Results.csv',
             mime='text/csv',
             )
        uu1, uu2 = st.columns(2)
        with uu2:
            with st.expander("Original Data"):
                fig.update_layout(width=580)
                st.plotly_chart(fig)
        with uu1:
            with st.expander("Averaged Curve Sliced Data"):
                avg_plt.update_layout(width=580)
                st.plotly_chart(avg_plt)
    
