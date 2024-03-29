


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

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

@st.cache(allow_output_mutation=True)
def get_r2_numpy_corrcoef(x, y):
    return np.corrcoef(x, y)[0, 1]**2
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

#@st.experimental_memo(suppress_st_warning=True)
def processing(uploaded_file, needlesize):
        needlesize = needlesize
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
        wadmax = wad['Amplitude - Normalized Pressure Data'].idxmax()
        wadmin = wad['Amplitude - Normalized Pressure Data'].idxmin()
        fir_curve = wad['Amplitude - Normalized Pressure Data'].iloc[wadmax:wadmin-800]
        sec_curve = wad['Amplitude - Normalized Pressure Data'].iloc[wadmin:]
        avg_curve = (fir_curve.reset_index(drop=True) + sec_curve[:len(fir_curve)].reset_index(drop=True)) / 2
        avg_curve1 = pd.DataFrame()
        avg_curve1['Amplitude - Normalized Pressure Data'] = sec_curve
        if filt_type == 'Rolling':
            avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve1['Amplitude - Normalized Pressure Data'].rolling(window = avg_filt).mean()
        if filt_type == 'Exponentially Weighted':
            avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve1['Amplitude - Normalized Pressure Data'].ewm(span = avg_filt).mean()
        last_point = avg_curve1['Amplitude - Normalized Pressure Data'].iloc[-1]
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
        avg_curve1['Amplitude - Normalized Pressure Data'] = avg_curve1['Amplitude - Normalized Pressure Data']
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

        
        cur['Average curve mmHg'] = cur['Averaged Curve'].rolling(window=1000).mean()
        lastcur = cur['Average curve mmHg'].iloc[-1]
        cur['Average curve mmHg'] =cur['Average curve mmHg'] - lastcur
        md = max(avg_curve1['Amplitude - Normalized Pressure Data'])
        first = avg_curve1['Amplitude - Normalized Pressure Data'] 
        last = avg_curve1['Amplitude - Normalized Pressure Data'].iloc[-1] 
        are = avg_curve1['Amplitude - Normalized Pressure Data'] * 0.001
        totalarea = are.sum()
        curve =  first - last
        length = 3.81 * 10**-2
        if needlesize == 12:
            R = (1.26 * 10**-9)
        if needlesize == 13:
                R = (7.33 * 10**-10)
        if needlesize == 14:
                R = (5.12 * 10**-10)
        if needlesize == 15:
                R = (3.23 * 10**-10)
        if needlesize == 16:
                R = (2.13 * 10**-10)
                length = (3.81 * 10**-2)
        if needlesize == 17:
                R = (1.52 * 10**-10)
                radius = 0.419 / 1000  
        if needlesize == 17.5:
                R = (1.25*10**-10)
                radius = 0.419 / 1000  
                length = 0.2286
        if needlesize == 18:
                R = (6.712* 10**-11)
                radius = 0.419 / 1000
        if needlesize == 18.5:
                R = (4.425 * 10**-10)
                radius = 0.419 / 1000
                length = (2.54 * 10**-1)
        if needlesize == 19:
                R = (4.04 * 10**-11)
                radius = 0.343 / 1000
        if needlesize == 20:
                R = (2.75 * 10**-11)
                radius = 0.302 / 1000

        Q = (((0.6 * (first * 0.001)) / totalarea) / 0.001) * (1*10**-6)
        shear = 4*(Q/(pi*(R)))
        avg_curve1['Shear Rate'] = shear
        avg_curve1['Flow'] = Q
        avg_curve1['Relative Resistance to Flow'] = 0.000000017591156283221753 / avg_curve1['Flow']
            
        avg_curve1['Shear Stress'] = (avg_curve1['Amplitude - Normalized Pressure Data'] * 133322).diff().abs() / 4
        avg_curve1['Viscosity'] = (avg_curve1['Shear Stress'] / (length *2)) / avg_curve1['Shear Rate']

        rrf = avg_curve1
        del avg_curve
        del dataframe
        return rrf, avg_curve1, cur, wad


with st.sidebar:
    # Sidebar
    menu = option_menu(None, ["Home", "Records", "Test Analytics", 'Shear Rate and RRF', 'Data'], 
    icons=['house',  "list-task", 'graph-up', 'moisture', 'table'], 
    menu_icon="cast", default_index=0, orientation="vertical")

#tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home","💉 Run Test", "📈 Test Analytics", "🩸 Shear Rate and RRF Analytics", "🗃 Data"])

if menu == 'Home':  
    # Home page
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
    with st.expander("How to Intepret Analytics"):
        st.markdown("- Relative resistance to flow represents the relative difference between the fluid of interest and water controls")
        st.markdown("- Shear rate flow time represents the amount of time the fluid takes to flow from a given shear rate")
        st.markdown("- The graph with the orange line displays the relationship between shear rate and relative resistance to flow")
        st.markdown("- The graph with the red and blue lines displays the relationship between a given fluid and water plus the relationship with time and pressure")
    with st.expander("Device Usage Tutorial"):
           st.markdown("![Alt Text](https://github.com/chags1313/graphs/blob/main/ezgif.com-gif-maker%20(5).gif?raw=true)")

with st.sidebar:
    # additional sidebar
    with st.expander("Admin Settings"):

        needlesize = st.number_input('Needle Size', value=17.5, step=0.5)
        filt_type = st.selectbox('Filter Type', options = ['Rolling', 'Exponentially Weighted'])
        avg_filt = st.number_input('Averaging Filter',value = 10, step=1)

    uploaded_file = st.sidebar.file_uploader("Upload Your RPR Test File", type="csv")

    if uploaded_file is not None:
    
        rrf, avg_curve1, cur, wad = processing(uploaded_file = uploaded_file,needlesize = needlesize)

if menu == "Records":
    # past records
    colored_header("Records")
    result = db.fetch().items
    db_df = pd.DataFrame(result)
    dd = db_df.reindex(sorted(db_df.columns), axis=1)
    slct_rcd = st.multiselect("", options = db_df['record_id'], help='Previous records are stored with a record id corresponding the file name analyzed')
    for rcds in slct_rcd:
        colored_header(rcds)
        dta = dd[dd['record_id'] == rcds].iloc[-1]
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
    # test analytics page
    try:
        colored_header("Raw Test Data and Sliced Curves")
        uu1, uu2 = st.columns(2)
        wad['Pressure (mmHg)'] = wad['Amplitude - Normalized Pressure Data']
        fig =  px.scatter(wad, y='Pressure (mmHg)',x= "Seconds", color = 'curves',color_discrete_sequence=["gray", "red"])
        avg_curve1['analyzed'] = avg_curve1['Shear Rate'] < 500
        avg_curve1['Seconds'] = avg_curve1.index / 1000
        avg_curve1['Pressure (mmHg)'] = avg_curve1["Amplitude - Normalized Pressure Data"]
        avg_plt = px.line(avg_curve1, y = 'Pressure (mmHg)',x = 'Seconds', color = 'analyzed', color_discrete_sequence=['red', 'purple'])#color_discrete_sequence=['black'])

        with uu2:
            #with st.expander("Averaged Curve Sliced Data"):
            rsq = get_r2_numpy_corrcoef(x=cur['First Curve'], y=cur['Second Curve'])
            rsq = round(rsq, 3)
            st.info('R Squared: ' + str(rsq), icon ='📊')
            avg_plt.update_layout(showlegend=False, hovermode='x unified')
            avg_plt.add_hline(y=0.0, line_width=3, line_dash="dash")
            st.plotly_chart(avg_plt, config= dict(
        displayModeBar = False), use_container_width=True)

        with uu1:
            #with st.expander("Original Data"):
            if rsq > 0.9:
                st.success("Valid Test", icon='✅')
            else:
                st.error("Invalid Test - Try Running Test Again", icon ='❌')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, config= dict(
            displayModeBar = False, staticPlot= True), use_container_width=True)
            st.write("Autocorrelation: " + str(round(cur['Second Curve'].autocorr(lag=1000), 4)))
        
    except:
            st.warning("Upload data", icon ='📁')

if menu == "Shear Rate and RRF":
    try:
        colored_header("Relative Resistance to Flow by Shear Rate")
        rrf = rrf[rrf['Shear Rate'] > 0.01]
        rrf['Pressure - mmHg'] = rrf['Amplitude - Normalized Pressure Data']
        rrf2 = rrf
        rrf2['Time in Seconds'] = rrf2.reset_index(drop=True).index / 1000
        rrf2 = rrf2[rrf2['Shear Stress'] !=0]
        rrf2 = rrf2[rrf2['Viscosity'] !=0]
        rrf2['Viscosity'] = rrf2['Viscosity'].round(16)
        
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
        def create_kpi(data, txt, min_range, max_range, standard):
            st.text(txt)
            f = data[data['Shear Rate'] > min_range]
            f = f[f['Shear Rate'] < max_range]
            f1 = len(f['Viscosity']) / (max_range - min_range) / standard
            f1 = f1 
            f1 = round(f1, 2)
            if f1 > 10:
                kpi = st.error(str(f1), icon = '🔴')
            else:
                kpi = st.info(str(f1), icon = '🔵')
            return kpi
        def pressure_kpi(data, txt, min_range, max_range, standard):
            st.text(txt)
            f = data[data['Shear Rate'] > min_range]
            f = f[f['Shear Rate'] < max_range]
            f1 = f['Pressure - mmHg'].mean()
            f1 = f1 
            f1 = round(f1, 2)
            if f1 > 10:
                kpi = st.error(str(f1), icon = '🔴')
            else:
                kpi = st.info(str(f1), icon = '🔵')
            return kpi
        def visc_kpi(data, txt, min_range, max_range, standard):
            st.text(txt)
            f = data[data['Shear Rate'] > min_range]
            f = f[f['Shear Rate'] < max_range]
            f1 = f['Viscosity'].mean()
            f1 = f1 
            f1 = round(f1, 2)
            if f1 > 10:
                kpi = st.error(str(f1), icon = '🔴')
            else:
                kpi = st.info(str(f1), icon = '🔵')
            return kpi
            

        
        f = rrf2[rrf2['Shear Rate'] > 450]
        f = f[f['Shear Rate'] < 550]
        standard = len(f['Viscosity']) / 100
        rrf2['Relative Viscosity'] = rrf2['Viscosity'] / standard
        with c8:
            create_kpi(rrf2, txt="400-s Relative Viscosity", min_range=350, max_range=450, standard = standard)
        with c7:
            create_kpi(rrf2, txt="300-s Relative Viscosity", min_range=250, max_range=350, standard = standard)
        with c6:
            create_kpi(rrf2, txt="200-s Relative Viscosity", min_range=150, max_range=250, standard = standard)
        with c5:
            create_kpi(rrf2, txt="100-s Relative Viscosity", min_range=50, max_range=150, standard = standard)
        with c4:
            create_kpi(rrf2, txt="50-s Relative Viscosity", min_range=0.1, max_range=100, standard = standard) 
        with c3:
            create_kpi(rrf2, txt="25-s Relative Viscosity", min_range=0.1, max_range=50, standard = standard)
        with c2:
            create_kpi(rrf2, txt="10-s Relative Viscosity", min_range=0.1, max_range=20, standard = standard)
        with c1:
            create_kpi(rrf2, txt="5-s Relative Viscosity", min_range=0.1, max_range=10, standard = standard)
        #db_upload(f=uploaded_file.name, z1=z1, y1=y1, x1=x1, o1=o1, p1=p1)
        rrf2['Time of Flow'] = rrf2.index / 1000
        stime = px.area(rrf2, x ='Shear Rate', y = 'Time in Seconds', color_discrete_sequence=['purple'])
        stime.update_layout(hovermode='x unified')
        stime.update_yaxes(range=(0,75))
        stime.update_xaxes(range=(0,500))
        st.plotly_chart(stime, config= dict(
            displayModeBar = False), use_container_width=True)

        colored_header("Data Exploration")
        slid = st.slider("Enter Shear Rate", min_value = 0.0, value = 0.0,max_value = 500.0, step = 0.5, help ='Enter a Shear Rate to Take a Deeper Look at the Data')
        rg = rrf2[rrf2['Shear Rate'] < slid + 0.49]
        rg = rg[rg['Shear Rate'] > slid - 0.49]
        st.dataframe(rg)

        colored_header("Shear Rate by Viscosity")
        c_1, c_2, c_3, c_4, c_5, c_6, c_7, c_8 = st.columns(8)
        with c_8:
            visc_kpi(rrf2, txt="400-s Viscosity", min_range=399, max_range=401, standard = 0.59)
        with c_7:
            visc_kpi(rrf2, txt="300-s Viscosity", min_range=299, max_range=301, standard = 0.44)
        with c_6:
            visc_kpi(rrf2, txt="200-s Viscosity", min_range=199, max_range=201, standard = 0.29)
        with c_5:
            visc_kpi(rrf2, txt="100-s Viscosity", min_range=99, max_range=101, standard = 0.15)
        with c_4:
            visc_kpi(rrf2, txt="50-s Viscosity", min_range=49.9, max_range=50.1, standard = 0.075)
        with c_3:
            visc_kpi(rrf2, txt="25-s Viscosity", min_range=24.9, max_range=25.1, standard = 0.038)
        with c_2:
            visc_kpi(rrf2, txt="10-s Viscosity", min_range=9.9, max_range=10.1, standard = 0.015)
        with c_1:
            visc_kpi(rrf2, txt="5-s Viscosity", min_range=4.9, max_range=5.1, standard = 0.0075)
        #db_upload(f=uploaded_file.name, z1=z1, y1=y1, x1=x1, o1=o1, p1=p1)
        shears = px.scatter(rrf, x='Shear Rate', y = 'Viscosity', color_discrete_sequence=['orange'])
        #shear.data = [t for t in shears.data if t.mode == "lines"] , trendline="lowess", trendline_options=dict(frac=0.5)
        #shears.update_traces(visible=False, selector=dict(mode="markers"))
        #shears.update_yaxes(range=(0,0.5))
        shears.update_xaxes(range=(5,500))
        shears.update_yaxes(range=(0,20))
        shears.update_layout(hovermode='x unified')
        e1, e2 = st.columns(2)
        with e1:
            st.plotly_chart(shears, config= dict(
            displayModeBar = False), use_container_width=True)
        with e2:
            rrf['Rate of Shear Rate Change'] = rrf['Shear Rate'].diff().abs()
            
            flowc = px.scatter(rrf, y ='Rate of Shear Rate Change', x = 'Shear Rate', color_discrete_sequence=['green'])
            flowc.update_layout(hovermode='x unified')
            #flowc.update_yaxes(range=(0,10000))
            flowc.update_xaxes(range=(0,500))
            st.plotly_chart(flowc, config= dict(
            displayModeBar = False), use_container_width=True)
        colored_header("Pressure by Shear Rate")
        rrf['Pressure Change'] = rrf['Pressure - mmHg'].diff().abs() * 133.32
        C1, C2, C3, C4, C5, C6, C7, C8 = st.columns(8)
        with C8:
            #create_kpi(rrf2, txt="400-s Relative Viscosity", min_range=350, max_range=450, standard = standard)
            pressure_kpi(rrf2, txt="400-s Pressure", min_range=399, max_range=401, standard = 0.59)
        with C7:
            #create_kpi(rrf2, txt="300-s Relative Viscosity", min_range=250, max_range=350, standard = standard)
            pressure_kpi(rrf2, txt="300-s Pressure", min_range=299, max_range=301, standard = 0.44)
        with C6:
            #create_kpi(rrf2, txt="200-s Relative Viscosity", min_range=150, max_range=250, standard = standard)
            pressure_kpi(rrf2, txt="200-s Pressure", min_range=199, max_range=201, standard = 0.29)
        with C5:
            #create_kpi(rrf2, txt="100-s Relative Viscosity", min_range=50, max_range=150, standard = standard)
            pressure_kpi(rrf2, txt="100-s Pressure", min_range=99, max_range=101, standard = 0.15)
        with C4:
            #create_kpi(rrf2, txt="50-s Relative Viscosity", min_range=0.1, max_range=100, standard = standard) 
            pressure_kpi(rrf2, txt="50-s Pressure", min_range=49.9, max_range=50.1, standard = 0.075)
        with C3:
            #create_kpi(rrf2, txt="25-s Relative Viscosity", min_range=0.1, max_range=50, standard = standard)
            pressure_kpi(rrf2, txt="25-s Pressure", min_range=24.9, max_range=25.1, standard = 0.038)
        with C2:
            #create_kpi(rrf2, txt="10-s Relative Viscosity", min_range=0.1, max_range=20, standard = standard)
            pressure_kpi(rrf2, txt="10-s Pressure", min_range=9.9, max_range=10.1, standard = 0.015)
        with C1:
            #create_kpi(rrf2, txt="5-s Relative Viscosity", min_range=0.1, max_range=10, standard = standard)
            pressure_kpi(rrf2, txt="5-s Pressure", min_range=4.9, max_range=5.1, standard = 0.0075)
        preshear = px.area(rrf, x='Shear Rate', y = 'Pressure - mmHg', color_discrete_sequence=['black'])
        preshear.update_xaxes(range=(0,500))
        st.plotly_chart(preshear, config= dict(
            displayModeBar = False),use_container_width=True)
        
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





           

        
