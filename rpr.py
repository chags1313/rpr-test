


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
import streamlit.components.v1 as components
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

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home","💉 Run Test", "📈 Test Analytics", "🩸 Shear Rate and RRF Analytics", "🗃 Data"])

with tab1:  
    st.title("Rapid Profile Rheometer 🩸")
    st.write("Biofluid Technology LLC")
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
    components.iframe("http://desktop-kvcjuh6.localdomain:8000/rpr2.html")
            
with tab3:
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
        avg_curve1['Amplitude - Normalized Pressure Data'] = sec_curve
        last_point = avg_curve1['Amplitude - Normalized Pressure Data'].iloc[-1]
        #avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve1['Amplitude - Normalized Pressure Data'] -  1.1
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

        df_melt = cur.melt(id_vars="Time", value_vars=['First Curve', 'Second Curve', 'Averaged Curve']) 
        colored_header("Raw Test Data and Sliced Curves")
        uu1, uu2 = st.columns(2)
        fig =  px.scatter(wad, y='Amplitude - Normalized Pressure Data',x= "Seconds", color = 'curves',color_discrete_sequence=["gray", "red"])
        
        
        #cur['flow'] = cur['Flow'].rolling(window= 1000).mean().diff()
        #cur['shear rate'] = cur['Shear Rate'].rolling(window=1000).mean()
        cur['Average curve mmHg'] = cur['Averaged Curve'].rolling(window=100).mean()
        lastcur = cur['Average curve mmHg'].iloc[-1]
        cur['Average curve mmHg'] =cur['Average curve mmHg'] - lastcur
        
        avg_plt = px.line(cur, x= 'Time',y = "Average curve mmHg", color_discrete_sequence=['black'])

        with uu2:
            #with st.expander("Averaged Curve Sliced Data"):
            rsq = get_r2_numpy_corrcoef(x=cur['First Curve'], y=cur['Second Curve'])
            rsq = round(rsq, 3)
            st.info('R Squared: ' + str(rsq))
            avg_plt.update_layout(width=480, showlegend=False, hovermode='x unified')
            st.plotly_chart(avg_plt, config= dict(
        displayModeBar = False))

        with uu1:
            #with st.expander("Original Data"):
            if rsq > 0.9:
                st.success("Valid Test")
            else:
                st.error("Invalid Test - Try Running Test Again")
            fig.update_layout(width=480,showlegend=False)
            st.plotly_chart(fig, config= dict(
        displayModeBar = False, staticPlot= True))
        
         

with tab4:
    if uploaded_file is not None:
        md = max(avg_curve1['Amplitude - Normalized Pressure Data'])
        with st.spinner("Processing Analytics"):
             for i in range(len(avg_curve1)):
                 first = avg_curve1['Amplitude - Normalized Pressure Data'].iloc[i] 
                 last = avg_curve1['Amplitude - Normalized Pressure Data'].iloc[-1] 
                 curve =  first - last
                 if needlesize == 12:
                    Q = ((((0.6 * curve)/ md) / time)) * (1.26 * 10**-9)
                 if needlesize == 13:
                        Q = ((((0.6 * curve)/md) / time)) * (7.33 * 10**-10)
                 if needlesize == 14:
                        Q = ((((0.6 * curve)/md) / time)) * (5.12 * 10**-10)
                 if needlesize == 15:
                        Q = ((((0.6 * curve)/md) / time)) * (3.23 * 10**-10)
                 if needlesize == 16:
                        Q = ((((0.6 * curve)/md) / time)) * (2.13 * 10**-10)
                 if needlesize == 17:
                        Q = ((((0.6 * curve)/md) / time)) * (1.52 * 10**-10)  
                 if needlesize == 18:
                        Q = ((((0.6 * curve)/md) / time)) * (7.36 * 10**-11)
                 if needlesize == 19:
                        Q = ((((0.6 * curve)/md) / time)) * (4.04 * 10**-11)
                 if needlesize == 20:
                        Q = ((((0.6 * curve)/md) / time)) * (2.74 * 10**-11)
                 else:
                    Q = ((((0.6 * curve) / md) / time)) * (1*10**-6)
                 shear = 4*(Q/(pi*(R**3)))
                 print(shear)
                 avg_curve1['shear'].iloc[i] = shear
                 avg_curve1['flow'].iloc[i] = Q

        cur['Shear Rate'] = avg_curve1['shear']
        cur['Flow'] = avg_curve1['flow']
        

        
        bld = list()
        num = list()
        shr = list()
        last_point = cur['Averaged Curve'].iloc[-1]
        cur['Averaged Curve'] = cur['Averaged Curve'] -  last_point
        for numbers in reversed(np.arange(0.02, 50.01, 0.01)):
            u1 = cur[cur['Second Curve'] < numbers]
            z1 = cur[cur['Second Curve'] < numbers - 0.01]
            bld.append((len(u1) - len(z1))/ 1000) 
            num.append(numbers)
            z = avg_curve1[avg_curve1['Amplitude - Normalized Pressure Data'] < numbers]
            z = z[z['Amplitude - Normalized Pressure Data'] > (numbers - 0.01)]
            shr.append((z['shear'].mean()))
        rrf = pd.DataFrame({'Blood Sample': bld})
        rrf['Water Control'] = np.full(shape=len(bld),fill_value=0.009,dtype=np.float) 
        rrf['Relative Resistance to Flow'] = 'na'
        rrf['mmHg range'] = 'na'
        rrf['mmHg'] = num
        rrf['Shear Rate'] = shr
        rrf['Shear Rate'] = rrf['Shear Rate'].abs()
        for i in range(len(rrf)):
            rrf['Relative Resistance to Flow'].iloc[i] = rrf['Blood Sample'].iloc[i] / rrf['Water Control'].iloc[i]
            high = round(rrf['mmHg'].iloc[i],2)
            low = round(rrf['mmHg'].iloc[i] - 0.01,2)
            rrf['mmHg range'].iloc[i] = str(high) + " to " + str(low)
        colored_header("Processed Test Data")

        

    
        c1, c2, c3, c4, c5 = st.columns(5)
        with c5:
            st.text("500 to 1000 -s Shear Rate RRF")
            p = rrf[rrf['Shear Rate'] > 1000]
            p = p[p['Shear Rate'] < 500]
            p1 = p['Relative Resistance to Flow'].mean()
            p1 = round(p1, 2)
            st.info(str(p1)) 
        with c4:
            st.text("300 to 500 -s Shear Rate RRF")
            o = rrf[rrf['Shear Rate'] > 300]
            o = o[o['Shear Rate'] < 500]
            o1 = o['Relative Resistance to Flow'].mean()
            o1 = round(o1, 2)
            st.info(str(o1)) 
        with c3:
            st.text("100 to 300 -s Shear Rate RRF")
            x = rrf[rrf['Shear Rate'] > 100]
            x = x[x['Shear Rate'] < 300]
            x1 = x['Relative Resistance to Flow'].mean()
            x1 = round(x1, 2)
            st.success(str(x1)) 
        with c2:
            st.text("10 to 20 -s Shear Rate RRF")
            y = rrf[rrf['Shear Rate'] > 10]
            y = rrf[rrf['Shear Rate'] < 20]
            y1 = y['Relative Resistance to Flow'].mean()
            y1 = round(y1, 2)
            st.warning(str(y1))
        with c1:
            st.text("0 to 10-s Shear Rate RRF")
            z = rrf[rrf['Shear Rate'] > 0]
            z = rrf[rrf['Shear Rate'] < 10]
            z1 = z['Relative Resistance to Flow'].mean()
            z1 = round(z1, 2)
            st.error(str(z1))
            
        e1, e2 = st.columns(2)
     
        
        #rrf['Shear Rate'] = rrf['Shear Rate'].rolling(window=10).mean()
        rrf = rrf[rrf['Blood Sample'] != 0]
        shears = px.scatter(rrf, x='Shear Rate', y='Relative Resistance to Flow', color_discrete_sequence=['orange'],hover_data=["mmHg range", "Blood Sample", "Water Control"])
        #shear.data = [t for t in shears.data if t.mode == "lines"] trendline="lowess", trendline_options=dict(frac=0.09)
        shears.update_yaxes(range=(0,100))
        shears.update_xaxes(range=(0,500))
        shears.update_layout(width=525, hovermode='x unified')
        with e1:
            st.plotly_chart(shears, config= dict(
            displayModeBar = False))
             

        shears1 = px.line(rrf,x = 'mmHg range',  y=['Blood Sample', 'Water Control'], color_discrete_sequence=['red', 'blue'], markers=True, hover_data=['Shear Rate', 'Relative Resistance to Flow'])
        shears1.update_layout(yaxis_title="Time of Flow in Seconds",showlegend=False, width=525, hovermode='x unified')
        shears1.update_yaxes(range=(0,5))
        with e2:
            st.plotly_chart(shears1, config= dict(
            displayModeBar = False))
    else:
            st.info("Upload data in analytics tab")
with tab5:
    if uploaded_file is not None:
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
                st.dataframe(rrf.drop(['Water Control'], axis=1).dropna().style.highlight_min(axis=0))
            with dfcol2:
                st.download_button(
                    label="Download Processed Curves",
                    data=csv2,
                    file_name='Results.csv',
                    mime='text/csv',
                    )
                cur1 = cur.drop(['Flow', 'Average curve mmHg'], axis=1)
             ##   cur1 = cur1.abs()
                st.dataframe(cur1)

    else:
            st.info("Upload data in analytics tab")
