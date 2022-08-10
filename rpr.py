


import streamlit as st
from io import StringIO
import pandas as pd
import plotly.express as px
import numpy as np
import base64




filen = 0

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
#samplesAvailable = None

st.set_page_config(layout="wide")


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 




#st.title("RPR Analysis")

tab1, tab2, tab3 = st.tabs(["🏠 Home","📈 Analytics", "🗃 Compare"])



with tab1:  
    st.title("Rapid Profile Rheometer 🩸")
    st.write("Biofluid Technology LLC")
    st.markdown("A device for differential diagnosis of inflammatory and hematologic disorders.")
    with st.expander("How to Run a Test"):
        st.markdown("1. On the test tab, click run test")
        st.markdown("2. Pull up plunger.. wait for the fluid to settle in tube")
        st.markdown("3. Push down plunger.. wait for the fluid to settle in tube")
        st.markdown("4. Once fluid settles, click stop test")
        st.markdown("5. Navigate to the analytics tab to view results")
    with st.expander("How to Intepret Analaytics"):
        st.markdown("- Relative resistance to flow represents the relative difference between the fluid of interest and water controls")
        st.markdown("- Shear rate flow time represents the amount of time the fluid takes to flow from a given shear rate")
        st.markdown("- The graph with the orange line displays the relationship between shear rate and relative resistance to flow")
        st.markdown("- The graph with the red and blue lines displays the relationship between a given fluid and water plus the relationship with time and pressure")
    with st.expander("Device Usage Tutorial"):
            st.markdown("![Alt Text](https://github.com/chags1313/graphs/blob/main/ezgif.com-gif-maker%20(5).gif?raw=true)")
    
            


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
            st.text("100 -s Shear Rate RRF")
            st.info(str((len(cur[cur['Shear Rate'] < 100]) / 1000)) + " seconds") 
        with c2:
            st.text("10 -s Shear Rate RRF")
            st.info(str((len(cur[cur['Shear Rate'] < 5]) / 1000)) + " seconds")
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
            st.plotly_chart(shears, config= dict(
            displayModeBar = False))
             
             
        shears1 = px.scatter(rrf,x = 'mmHg',  y=['Blood Sample', 'Water Control'], color_discrete_sequence=['red', 'blue'])
        shears1.update_layout(yaxis_title="Time of Flow in Seconds")
        with e2:
            st.plotly_chart(shears1, config= dict(
            displayModeBar = False))
        #xx1, xx2 = st.columns(2)
     
        #with xx1:
            #st.dataframe(rrf[['Shear Rate','Relative Resistance to Flow', 'mmHg range']].dropna().style.background_gradient(cmap='Greens', subset=['Shear Rate','Relative Resistance to Flow']), height=1000)
            #aggrid_interactive_table(df=rrf[['Shear Rate','Relative Resistance to Flow', 'mmHg range']])

        @st.cache
        def convert_df(df):
         # IMPORTANT: Cache the conversion to prevent computation on every rerun
             return df.to_csv().encode('utf-8')

        csv = convert_df(rrf)
        #with xx2:
         #   st.text("High Shear Rate")
          #  hsr = max(rrf['Shear Rate'])
           # st.warning(str(round(hsr, 2)) + " -s")
            #st.text("Low Relative Resistance to Flow")
            #hi = min(rrf['Relative Resistance to Flow'])
            #st.warning(str(round(hi, 2)))
            #st.text("Low Shear Rate")
            #lsr = min(rrf['Shear Rate'])
            #st.error(str(round(lsr, 2)) + " -s")
            #st.text("High Relative Resistance to Flow")
            #lo = max(rrf['Relative Resistance to Flow'])
            #st.error(str(round(lo, 2)))
            


            
            

        uu1, uu2 = st.columns(2)
        with uu2:
            with st.expander("Original Data"):
                fig.update_layout(width=580)
                st.plotly_chart(fig)
        with uu1:
            with st.expander("Averaged Curve Sliced Data"):
                avg_plt.update_layout(width=580)
                st.plotly_chart(avg_plt)
        st.text("Save All Data")
        st.download_button(
         label="Download data as CSV",
         data=csv,
         file_name='Results.csv',
         mime='text/csv',
         )

        def create_download_link(val, filename):
            b64 = base64.b64encode(val)  # val looks like b'...'
            return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

with tab3:  


    uploaded_file1 = st.file_uploader("Upload RPR Analytics Files", type="csv", accept_multiple_files=True)
    if uploaded_file1 is not None:
        
                # To read file as bytes:
                for file in uploaded_file1:
                     dataframe = pd.read_csv(file)
                     dataframe['Date and Time of Test'] = str(uploaded_file1.name)
                     file.seek(0)
                     com1 = pd.concat([com1, dataframe])
    
                rrfdate = px.box(com1, x= 'Date and Time of Test', y = 'Relative Resistance to Flow', color_discrete_sequence=['purple'])
                #rrfdate.update_layout()
                rrfdate.update_xaxes(type='category')
                rrfdate.update_layout(width=1200)
                st.plotly_chart(rrfdate,config= dict(
                displayModeBar = False))
                sheardate = px.box(com1, x= 'Date and Time of Test', y = 'Shear Rate', color_discrete_sequence=['green'])
                #sheardate.update_layout()
                sheardate.update_xaxes(type='category')
                sheardate.update_layout(width=1200)
                st.plotly_chart(sheardate,config= dict(
                displayModeBar = False))
                com1['Flow Time in Seconds'] = com1['Blood Sample']
                comp = px.scatter(com1, x='mmHg range', y = 'Flow Time in Seconds', color = 'Date and Time of Test', color_continuous_scale=px.colors.sequential)
                comp.update_layout(width = 1200)
                st.plotly_chart(comp,config= dict(
                displayModeBar = False))
