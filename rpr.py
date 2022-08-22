


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
import base64
import itertools
#from pycaret.regression import setup, create_model, predict_model

@st.cache(allow_output_mutation=True)
def get_r2_numpy_corrcoef(x, y):
    return np.corrcoef(x, y)[0, 1]**2
#@st.cache(allow_output_mutation=True)
#def regression_model(data, target):
 #   dset = setup(data, target=target, silent=True)
  #  reg_model = create_model('et')
   # predictions = predict_model(reg_model, data = data)
    #return predictions, reg_model
@st.cache(allow_output_mutation=True)
def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

@st.cache(allow_output_mutation=True)
def convert_df(df):
    return df.to_csv().encode('utf-8')

HEADER_COLOR_CYCLE = itertools.cycle(
    [
        "#00c0f2",  # light-blue-70",
        "#ffbd45",  # "orange-70",
        "#00d4b1",  # "blue-green-70",
        "#1c83e1",  # "blue-70",
        "#803df5",  # "violet-70",
        "#ff4b4b",  # "red-70",
        "#21c354",  # "green-70",
        "#faca2b",  # "yellow-80",
    ]
)
    
def colored_header(label, description=None, color=None):
    """Shows a header with a colored underline and an optional description."""
    st.write("")
    if color is None:
        color = next(HEADER_COLOR_CYCLE)
    st.subheader(label)
    st.write(
        f'<hr style="background-color: {color}; margin-top: 0; margin-bottom: 0; height: 3px; border: none; border-radius: 3px;">',
        unsafe_allow_html=True,
    )
    if description:
        st.caption(description)


#set page config
st.set_page_config(layout="wide",
        page_title="Biofluid RPR",
        page_icon="chart_with_upwards_trend")

#hide streamlit menu bar
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 




st.title("Biofluid Technology")

tab1, tab2, tab3 = st.tabs(["🏠 Home","📈 Analytics", "🗃 Data"])

with tab1:  
    st.title("Rapid Profile Rheometer 🩸")
    st.write("Biofluid Technology LLC")
    st.markdown("A device for differential diagnosis of inflammatory and hematologic disorders.")
    with st.expander("How to Run a Test"):
        st.markdown("1. On the test tab, click run test")
        st.markdown("2. Pull up plunger.. wait for the fluid to settle in tube")
        st.markdown("3. Push down plunger.. wait for the fluid to settle in tube")
        st.markdown("4. Once fluid settles, click stop test")
        st.markdown("5. Navigate to the results tab to view results")
        st.markdown("6. Click export data button")
        st.markdown("7. Save exported data as a .csv file")
        st.markdown("8. Upload data on the analytics tab of the rpr web application")
    with st.expander("How to Intepret Analaytics"):
        st.markdown("- Relative resistance to flow represents the relative difference between the fluid of interest and water controls")
        st.markdown("- Shear rate flow time represents the amount of time the fluid takes to flow from a given shear rate")
        st.markdown("- The graph with the orange line displays the relationship between shear rate and relative resistance to flow")
        st.markdown("- The graph with the red and blue lines displays the relationship between a given fluid and water plus the relationship with time and pressure")
    with st.expander("Device Usage Tutorial"):
           st.markdown("![Alt Text](https://github.com/chags1313/graphs/blob/main/ezgif.com-gif-maker%20(5).gif?raw=true)")
    with st.expander("Device Parameters"):
        needlesize = st.number_input('Insert the needle size', value = 16)
    
            
with tab2:
    uploaded_file = st.file_uploader("Upload Your RPR Test File", type="csv")

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        string_data = stringio.read()
        dataframe = pd.read_csv(uploaded_file)
        
        fv = dataframe['Amplitude - Normalized Pressure Data'].iloc[1]
        dataframe = dataframe - fv
        dataframe['Seconds'] = dataframe.index / 1000
        wad = dataframe
        #wad['Amplitude - Normalized Pressure Data'] = wad[0]
        wadmax = wad['Amplitude - Normalized Pressure Data'].idxmax()
        wadmin = wad['Amplitude - Normalized Pressure Data'].idxmin()
        fir_curve = wad['Amplitude - Normalized Pressure Data'].iloc[wadmax:wadmin-800]
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
        lastpav = avg_curve1['Amplitude - Normalized Pressure Data'].iloc[-1]
        avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve1['Amplitude - Normalized Pressure Data'] - lastpav
        avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve1['Amplitude - Normalized Pressure Data'].abs()
        shear = 4*(Q/(pi*(R**3)))
        fir_curve1 = pd.DataFrame(fir_curve)
        avg_curve1['shear'] = 'na'
        avg_curve1['flow'] = 'na'
        with st.spinner("Processing Analytics"):
             for i in range(len(avg_curve1)):
                 first = avg_curve1['Amplitude - Normalized Pressure Data'].iloc[i] 
                 last = avg_curve1['Amplitude - Normalized Pressure Data'].iloc[-1] 
                 curve =  first - last

                 Q = ((((0.6 * curve) / needlesize) / time)) * (1*10**-6)
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
        cur['Shear Rate'] = avg_curve1['shear'].abs()
        cur['Flow'] = avg_curve1['flow']
        df_melt = cur.melt(id_vars="Time", value_vars=['First Curve', 'Second Curve', 'Averaged Curve'])
        water = [
0.038333333,
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
            shr.append((z['shear'].mean()))
        rrf = pd.DataFrame({'Water Control': water})
        rrf['Blood Sample'] = bld
        rrf['Relative Resistance to Flow'] = 'na'
        rrf['mmHg range'] = 'na'
        rrf['mmHg'] = num
        rrf['Shear Rate'] = shr
        rrf['Shear Rate'] = rrf['Shear Rate'].abs()
        for i in range(len(rrf)):
            rrf['Relative Resistance to Flow'].iloc[i] = rrf['Blood Sample'].iloc[i] / rrf['Water Control'].iloc[i]
            high = rrf['mmHg'].iloc[i]
            low = rrf['mmHg'].iloc[i] - 0.5
            rrf['mmHg range'].iloc[i] = str(high) + " to " + str(low)
        colored_header("Processed Test Data")
        
        
        
        c1, c2, c3, c4 = st.columns(4)
        with c4:
            st.text("200 -s Shear Rate RRF")
            o = rrf[rrf['Shear Rate'] > 200]
            o = o[o['Shear Rate'] < 210]
            o1 = o['Relative Resistance to Flow'].tail(5).mean()
            o1 = round(o1, 2)
            st.info(str(o1)) 
        with c3:
            st.text("100 -s Shear Rate RRF")
            x = rrf[rrf['Shear Rate'] < 100]
            x = x[x['Shear Rate'] > 95]
            x1 = x['Relative Resistance to Flow'].head(5).mean()
            x1 = round(x1, 2)
            st.success(str(x1)) 
        with c2:
            st.text("10 -s Shear Rate RRF")
            y = rrf[rrf['Shear Rate'] < 10]
            y1 = y['Relative Resistance to Flow'].head(5).mean()
            y1 = round(y1, 2)
            st.warning(str(y1))
        with c1:
            st.text("5 -s Shear Rate RRF")
            z = rrf[rrf['Shear Rate'] < 5]
            z1 = z['Relative Resistance to Flow'].head(5).mean()
            z1 = round(z1, 2)
            st.error(str(z1))
            
        e1, e2 = st.columns(2)
     
        
        fig =  px.scatter(wad, y='Amplitude - Normalized Pressure Data',x= "Seconds", color = 'curves',color_discrete_sequence=["gray", "red"])
        
        
        cur['flow'] = cur['Flow'].rolling(window= 1000).mean().diff()
        cur['shear rate'] = cur['Shear Rate'].rolling(window=1000).mean()
        cur['Average curve mmHg'] = cur['Averaged Curve'].rolling(window=100).mean()
        lastcur = cur['Average curve mmHg'].iloc[-1]
        cur['Average curve mmHg'] =cur['Average curve mmHg'] - lastcur
        
        avg_plt = px.line(cur, x= 'Time',y = "Average curve mmHg", color_discrete_sequence=['black'])
        
        shears = px.scatter(rrf, x='Shear Rate', y='Relative Resistance to Flow', color_discrete_sequence=['orange'], trendline="lowess")
        shears.update_yaxes(range=(0,100))
        shears.update_xaxes(range=(0,100))
        shears.update_layout(width=525, hovermode='x')
        with e1:
            st.plotly_chart(shears, config= dict(
            displayModeBar = False))
             
             
        shears1 = px.line(rrf,x = 'mmHg range',  y=['Blood Sample', 'Water Control'], color_discrete_sequence=['red', 'blue'], markers=True)
        shears1.update_layout(yaxis_title="Time of Flow in Seconds",showlegend=False, width=525, hovermode='x unified')
        shears1.update_yaxes(range=(0,10))
        with e2:
            st.plotly_chart(shears1, config= dict(
            displayModeBar = False))

        
        colored_header("Raw Test Data and Sliced Curves")
        uu1, uu2 = st.columns(2)

        with uu2:
            with st.expander("Averaged Curve Sliced Data"):
                rsq = get_r2_numpy_corrcoef(x=cur['First Curve'], y=cur['Second Curve'])
                rsq = round(rsq, 3)
                st.info('R Squared: ' + str(rsq))
                avg_plt.update_layout(width=480, showlegend=False, hovermode='x')
                st.plotly_chart(avg_plt, config= dict(
            displayModeBar = False))

        with uu1:
            with st.expander("Original Data"):
                if rsq > 0.9:
                    st.success("Valid Test")
                else:
                    st.error("Invalid Test - Try Running Test Again")
                fig.update_layout(width=480,showlegend=False)
                st.plotly_chart(fig, config= dict(
            displayModeBar = False, staticPlot= True))
        colored_header(" ")
         


with tab3:
    if uploaded_file is not None:
            ##Running regression model predictions on data
           # pred, model = regression_model(data=rrf[['Shear Rate', 'Relative Resistance to Flow']], target = 'Relative Resistance to Flow')
            #r1 = pd.DataFrame()
            #r1['Shear Rate'] = np.arange(1,201)
            #r2 = predict_model(model, data = r1)

#            colored_header("Shear Rate by Relative Resistance to Flow Regression Model")
 #           cc1, cc2, cc3, cc4 = st.columns(4)
  #          r2['Shear Rate Prediction'] = r2['Label']
   #         pred_ch = px.line(r2, y='Shear Rate Prediction', x='Shear Rate', color_discrete_sequence=['purple'])
    #        pred_ch.update_yaxes(range=(0,100))
     #       pred_ch.update_layout(width=1000, showlegend=False)
      #      st.plotly_chart(pred_ch, config= dict(
       #         displayModeBar = False))

        #    rrf200s = r2[r2['Shear Rate'] == 100]
         #   rrf200s = round(rrf200s['Label'].iloc[0], 2)      
          #  rrf100s = r2[r2['Shear Rate'] == 100]
           # rrf100s = round(rrf100s['Label'].iloc[0], 2)
           # rrf10s = r2[r2['Shear Rate'] == 10]
           # rrf10s = round(rrf10s['Label'].iloc[0], 2)
           # rrf1s = r2[r2['Shear Rate'] == 1]
           # rrf1s = round(rrf1s['Label'].iloc[0], 2)
            
            #with cc4:
            #    st.text("200-s RRF Prediction")
            #    rrf_200s = st.info(str(rrf200s)) 
            #with cc3:
            #    st.text("100-s RRF Prediction")
            #    rrf_100s = st.success(str(rrf100s)) 
            #with cc2:
            #    st.text("10-s RRF Prediction")
            #    rrf_10s = st.warning(str(rrf10s))
            #with cc1:
             #   st.text("1-s RRF Prediction")
              #  rrf_1s = st.error(str(rrf1s))
            csv = convert_df(rrf)
            csv2 = convert_df(cur)


            dfcol1, dfcol2 = st.columns(2)
            with dfcol1:
                st.download_button(
                    label="Download Processed Shear Rate and RRF",
                    data=csv,
                    file_name='Results.csv',
                    mime='text/csv',
                    )
                st.dataframe(rrf.style.highlight_max(axis=0))
            with dfcol2:
                st.download_button(
                    label="Download Processed Curves",
                    data=csv2,
                    file_name='Results.csv',
                    mime='text/csv',
                    )
                st.dataframe(cur.style.highlight_max(axis=0))

       # uploaded_file1 = st.file_uploader("Upload RPR Analytics Files", type="csv", accept_multiple_files=True)
        #if uploaded_file1 is not None:

                    # To read file as bytes:
         #           for file in uploaded_file1:
          #               dataframe = pd.read_csv(file)
           #              dataframe['Analyitics File'] = str(file.name)
            #             file.seek(0)
             #            com1 = pd.concat([com1, dataframe])

              #      rrfdate = px.box(com1, x= 'Analyitics File', y = 'Relative Resistance to Flow', color_discrete_sequence=['purple'])
                    #rrfdate.update_layout()
               #     rrfdate.update_xaxes(type='category')
                #    rrfdate.update_layout(width=1200)
                 #   st.plotly_chart(rrfdate,config= dict(
                  #  displayModeBar = False))
                   # sheardate = px.box(com1, x= 'Analyitics File', y = 'Shear Rate', color_discrete_sequence=['green'])
                    #sheardate.update_layout()
                    #sheardate.update_xaxes(type='category')
                    #sheardate.update_layout(width=1200)
                    #st.plotly_chart(sheardate,config= dict(
                    #displayModeBar = False))
                    #com1['Flow Time in Seconds'] = com1['Blood Sample']
                    #comp = px.scatter(com1, x='mmHg range', y = 'Flow Time in Seconds', color = 'Analyitics File', color_continuous_scale=px.colors.sequential)
                    #comp.update_layout(width = 1200)
                    #st.plotly_chart(comp,config= dict(
                    #displayModeBar = False))
    else:
            st.info("Upload data in analytics tab")
