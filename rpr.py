


# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Thu May 19 15:15:40 2022
@author: chags
"""

import streamlit as st
from streamlit_option_menu import option_menu
from io import StringIO
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import base64
import itertools
import streamlit.components.v1 as components
from deta import Deta


deta = Deta("b02l5gt3_MFtTQuHFmWUEofyrn54FjjnWxAevcaY1")
db = deta.Base("rrf")

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
@st.experimental_memo(suppress_st_warning =True)
def db_upload(f, z1, y1, x1, o1, p1):
    db.put({"5 -s Shear Rate RRF": str(z1), "10 -s Shear Rate RRF": str(y1), "100 -s Shear Rate RRF": str(x1), "200 -s Shear Rate RRF": str(o1), "500 -s Shear Rate RRF": str(p1), "record_id": f})
def zero_crossing(data):
    return np.where(np.diff(np.sign(np.array(data))))[0]

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

@st.experimental_memo(suppress_st_warning=True)
def processing(uploaded_file):
        bytes_data = uploaded_file.getvalue()
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        string_data = stringio.read()
        dataframe = pd.read_csv(uploaded_file)
        try:
            dataframe['Amplitude - Normalized Pressure Data'] = dataframe['Amplitude - Normalized Pressure Data']
        except:
            dataframe['Amplitude - Normalized Pressure Data'] = dataframe
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
        avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve1['Amplitude - Normalized Pressure Data'] 
        #####avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve1['Amplitude - Normalized Pressure Data'] - lastpav
        
        ### removing data less than zero for water
        #zeropoint = avg_curve1.index[zero_crossing(avg_curve1['Amplitude - Normalized Pressure Data'])]
        #print(zeropoint)
        #print(len(avg_curve1))
        #avg_curve1 = avg_curve1.iloc[:zeropoint[0],:]
        #print(len(avg_curve1))
        avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve1['Amplitude - Normalized Pressure Data'].abs()
        avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve1['Amplitude - Normalized Pressure Data'] - avg_curve1['Amplitude - Normalized Pressure Data'].iloc[-1]
        avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve1['Amplitude - Normalized Pressure Data'].abs()
        shear = 4*(Q/(pi*(R**3)))
        fir_curve1 = pd.DataFrame(fir_curve)
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

        
        cur['Average curve mmHg'] = cur['Averaged Curve'].rolling(window=100).mean()
        lastcur = cur['Average curve mmHg'].iloc[-1]
        cur['Average curve mmHg'] =cur['Average curve mmHg'] - lastcur
        md = max(avg_curve1['Amplitude - Normalized Pressure Data'])
        #with st.spinner("Processing Analytics"):
            #for i in range(len(avg_curve1)):
        first = avg_curve1['Amplitude - Normalized Pressure Data'] 
        last = avg_curve1['Amplitude - Normalized Pressure Data'].iloc[-1] 
        are = avg_curve1['Amplitude - Normalized Pressure Data'] * 0.001
        totalarea = are.sum()
        curve =  first - last
        if needlesize == 12:
            Q = ((((0.6 * curve)/ md / time))) * (1*10**-6)
            R = (1.26 * 10**-9)
        if needlesize == 13:
                Q = ((((0.6 * curve)/md / time))) * (1*10**-6)
                R = (7.33 * 10**-10)
        if needlesize == 14:
                Q = ((((0.6 * curve)/md / time))) * (1*10**-6)
                R = (5.12 * 10**-10)
        if needlesize == 15:
                Q = ((((0.6 * curve)/md / time))) * (1*10**-6)
                R = (3.23 * 10**-10)
        if needlesize == 16:
                Q = ((((0.6 * curve)/md / time))) * (1*10**-6)
                R = (2.13 * 10**-10)
        if needlesize == 17:
                Q = ((((0.6 * curve)/md / time))) * (1*10**-6)
                R = (1.52 * 10**-10)  
        if needlesize == 18:
                Q = ((((0.6 * curve)/md / time))) * (1*10**-6)
                R = (7.36 * 10**-11)
                radius = 0.419 / 1000
        if needlesize == 19:
                Q = ((((0.6 * curve)/md / time))) * (1*10**-6)
                R = (4.04 * 10**-11)
                radius = 0.343 / 1000
        if needlesize == 20:
                Q = ((((0.6 * curve)/md / time)))* (1*10**-6)
                R = (2.75 * 10**-11)
                radius = 0.302 / 1000
        Q = (((0.6 * (first * 0.001)) / totalarea) / 0.001) * (1*10**-6)
        shear = 4*(Q/(pi*(R)))
        avg_curve1['Shear Rate'] = shear
        avg_curve1['Flow'] = Q
        avg_curve1['Relative Resistance to Flow'] = 0.000000017591156283221753 / avg_curve1['Flow']
        length = 3.81 * 10**-2
        avg_curve1['Shear Stress'] = (avg_curve1['Amplitude - Normalized Pressure Data'] * 133.32).diff().abs() * radius
        avg_curve1['Viscosity'] = (avg_curve1['Shear Stress'] / (length *2)) / avg_curve1['Shear Rate']
        #avg_curve1['Viscosity Equation 1'] = avg_curve1['Shear Stress'] / avg_curve1['Shear Rate']
        #avg_curve1['Viscosity Eq1'] = (avg_curve1['Shear Stress'] / avg_curve1['Shear Rate']).round(4)

        rrf = avg_curve1
        del avg_curve
        del dataframe
        return rrf, avg_curve1, cur, wad


#st.title("Biofluid Technology")
with st.sidebar:
    menu = option_menu(None, ["Home", "Records", "Test Analytics", 'Shear Rate and RRF', 'Data'], 
    icons=['house',  "list-task", 'graph-up', 'moisture', 'table'], 
    menu_icon="cast", default_index=0, orientation="vertical")

    

#tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home","💉 Run Test", "📈 Test Analytics", "🩸 Shear Rate and RRF Analytics", "🗃 Data"])

if menu == 'Home':  
    st.title("Rapid Profile Rheometer 🩸")
    st.write("Biofluid Technology Inc.")
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
    with st.expander("Needle Size"):
        needlesize = st.number_input(' ', value=20)
        st.write(needlesize)
with st.sidebar:
    uploaded_file = st.sidebar.file_uploader("Upload Your RPR Test File", type="csv")

    if uploaded_file is not None:
    
        rrf, avg_curve1, cur, wad = processing(uploaded_file = uploaded_file)

if menu == "Records":
    colored_header("Records")
    result = db.fetch().items
    db_df = pd.DataFrame(result)
    dd = db_df.reindex(sorted(db_df.columns), axis=1)
    slct_rcd = st.multiselect("", options = db_df['record_id'], help='Previous records are stored with a record id corresponding the file name analyzed')
    for rcds in slct_rcd:
        colored_header(rcds)
        dta = dd[dd['record_id'] == rcds].iloc[-1]
        #st.write(dta)
        met1, met2, met3, met4, met5 = st.columns(5)
        with met1:
            meta = float(dta['5 -s Shear Rate RRF'])
            st.write("5 -s Shear Rate RRF")
            if meta > 10:
                st.error(str(meta), icon='🔴')
            else:
                st.info(str(meta), icon = '🔵')
        with met2:
            metb = float(dta['10 -s Shear Rate RRF'])
            st.write("10 -s Shear Rate RRF")
            if metb > 10:
                st.error(str(metb), icon='🔴')
            else:
                st.info(str(metb), icon = '🔵')
        with met3:
            metc = float(dta['100 -s Shear Rate RRF'])
            st.write("100 -s Shear Rate RRF")
            if metc > 10:
                st.error(str(metc), icon='🔴')
            else:
                st.info(str(metc), icon = '🔵')
        with met4:
            metd= float(dta['200 -s Shear Rate RRF'])
            st.write("200 -s Shear Rate RRF")
            if metd > 10:
                st.error(str(metd), icon='🔴')
            else:
                st.info(str(metd), icon = '🔵')
        with met5:
            mete = float(dta['500 -s Shear Rate RRF'])
            st.write("500 -s Shear Rate RRF")
            if mete > 10:
                st.error(str(mete), icon='🔴')
            else:
                st.info(str(mete), icon = '🔵')
        #st.dataframe(dd[dd['record_id'] == rcds].iloc[-1])
            
if menu == "Test Analytics":

    try:
        colored_header("Raw Test Data and Sliced Curves")
        uu1, uu2 = st.columns(2)
        fig =  px.scatter(wad, y='Amplitude - Normalized Pressure Data',x= "Seconds", color = 'curves',color_discrete_sequence=["gray", "red"])
        
        avg_plt = px.line(avg_curve1, y = "Amplitude - Normalized Pressure Data", color_discrete_sequence=['black'])

        with uu2:
            #with st.expander("Averaged Curve Sliced Data"):
            rsq = get_r2_numpy_corrcoef(x=cur['First Curve'], y=cur['Second Curve'])
            rsq = round(rsq, 3)
            st.info('R Squared: ' + str(rsq), icon ='📊')
            avg_plt.update_layout(width=480, showlegend=False, hovermode='x unified')
            st.plotly_chart(avg_plt, config= dict(
        displayModeBar = False))

        with uu1:
            #with st.expander("Original Data"):
            if rsq > 0.9:
                st.success("Valid Test", icon='✅')
            else:
                st.error("Invalid Test - Try Running Test Again", icon ='❌')
            fig.update_layout(width=480,showlegend=False)
            st.plotly_chart(fig, config= dict(
            displayModeBar = False, staticPlot= True))
        
    except:
            st.warning("Upload data", icon ='📁')

if menu == "Shear Rate and RRF":
    try:


        
        colored_header("Processed Test Data")
        rrf = rrf[rrf['Flow'] != 0]
        rrf = rrf[rrf['Shear Rate'] > 0.05]
        rrf['Viscosity'] = rrf['Viscosity'].rolling(window=1000).mean()
        rrf['Viscosity'] = rrf['Viscosity'] * 1000
        


        c1, c2, c3, c4, c5 = st.columns(5)
        with c5:
            st.text("500-s Relative Viscosity")
            p = rrf[rrf['Shear Rate'] > 495]
            p = p[p['Shear Rate'] < 505]
            global p1
            p1 = p['Viscosity'].mean() 
            p1 = round(p1, 2)
            if p1 > 10:
                st.error(str(p1), icon = '🔴')
            else:
                st.info(str(p1), icon = '🔵')
        with c4:
            st.text("200-s Relative Viscosity")
            o = rrf[rrf['Shear Rate'] > 198]
            o = o[o['Shear Rate'] < 202]
            global o1
            o1 = o['Viscosity'].mean() 
            o1 = round(o1, 2)
            if o1 > 10:
                st.error(str(o1), icon = '🔴')
            else:
                st.info(str(o1), icon = '🔵')
        with c3:
            st.text("100-s Relative Viscosity")
            x = rrf[rrf['Shear Rate'] > 98]
            x = x[x['Shear Rate'] < 102]
            global x1
            x1 = x['Viscosity'].mean()
            x1 = round(x1, 2)
            if x1 > 10:
                st.error(str(x1), icon = '🔴')
            else:
                st.info(str(x1), icon = '🔵') 
        with c2:
            st.text("10-s Relative Viscosity")
            y = rrf[rrf['Shear Rate'] > 9.5]
            y = rrf[rrf['Shear Rate'] < 10.75]
            global y1
            y1 = y['Viscosity'].mean()  
            y1 = round(y1, 2)
            if y1 > 10:
                st.error(str(y1), icon = '🔴')
            else:
                st.info(str(y1), icon = '🔵')
        with c1:
            st.text("5-s Relative Viscosity")
            z = rrf[rrf['Shear Rate'] > 4.5]
            z = rrf[rrf['Shear Rate'] < 5.75]
            global z1
            z1 = z['Viscosity'].mean() 
            z1 = round(z1, 2)
            if z1 > 10:
                st.error(str(z1), icon = '🔴')
            else:
                st.info(str(z1), icon = '🔵')
        db_upload(f=uploaded_file.name, z1=z1, y1=y1, x1=x1, o1=o1, p1=p1)

            
        e1, e2 = st.columns(2)
     
        
        #rrf['Shear Rate'] = rrf['Shear Rate'].rolling(window=10).mean()
        #rrf = rrf[rrf['Blood Sample'] != 0]
        shears = px.scatter(rrf, x='Shear Rate', y = 'Viscosity', color_discrete_sequence=['orange'], trendline="lowess", trendline_options=dict(frac=0.5))
        #shear.data = [t for t in shears.data if t.mode == "lines"] 
        #shears.update_traces(visible=False, selector=dict(mode="markers"))
        shears.update_yaxes(range=(0,5))
        shears.update_xaxes(range=(0,500))
        shears.update_layout(width=525, hovermode='x unified')
        with e1:
            st.plotly_chart(shears, config= dict(
            displayModeBar = False))
        with e2:
            rrf['Pressure - mmHg'] = rrf['Amplitude - Normalized Pressure Data']
            flowc = px.histogram(rrf, x ='Flow')
            flowc.update_layout(width=525, hovermode='x unified')
            st.plotly_chart(flowc, config= dict(
            displayModeBar = False))



             


    except:
            st.warning("Upload data", icon='📁')
if menu == "Data":
    colored_header("Data")
    try:
            csv = convert_df(rrf)


            st.download_button(
                label="Download Processed Shear Rate and RRF",
                data=csv,
                file_name='Results.csv',
                mime='text/csv',
                )
            st.dataframe(rrf, width = 1000)
    except:
        st.warning("Upload data", icon = '📁')





           

        
