import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="Transjakarta Data Cleaning", layout="wide")
st.title("Transjakarta Data Cleaning & Analysis")

# 1. Load Data
df = pd.read_csv('Transjakarta.csv')
st.subheader("Raw Data (First & Last 3 Rows)")
st.dataframe(pd.concat([df.head(3), df.tail(3)]))

# 2. Data Info & Describe
with st.expander("Data Info & Describe"):
    buffer = io.StringIO()
    df.info(buf=buffer)
    st.text(buffer.getvalue())
    st.dataframe(df.describe())
    st.dataframe(df.describe(include='object'))

# 3. Unique Values per Column
with st.expander("Unique Values per Column"):
    listItem = []
    for col in df.columns:
        unique_sample = df[col].unique()[:5]
        # Convert to string for display
        unique_sample_str = [str(x) for x in unique_sample]
        listItem.append([col, df[col].nunique(), unique_sample_str])
    tabel1Desc = pd.DataFrame(columns=['Column Name', 'Number of Unique', 'Unique Sample'], data=listItem)
    st.dataframe(tabel1Desc)

# 4. Missing & Duplicate Values
col1, col2 = st.columns(2)
with col1:
    st.write("Missing Values (%)")
    st.dataframe((df.isna().sum()/df.shape[0]*100).to_frame('Missing %'))
with col2:
    st.write("Duplicate Rows Count")
    st.write(df.duplicated().sum())

# 5. Data Cleaning Steps
# Drop duplicates
df.drop_duplicates(inplace=True)
# Drop columns
df = df.drop(columns=['tapInStopsLat', 'tapInStopsLon', 'tapOutStopsLat', 'tapOutStopsLon', 'payCardName', 'transID', 'payCardName', 'stopEndSeq', 'stopStartSeq'])
# Fill corridorID by zipping with corridorName
corridor_map = dict(zip(df["corridorName"], df["corridorID"]))
df["corridorID"] = df["corridorName"].replace(corridor_map)
# Fill missing corridorID
corridor_nan = df.loc[df['corridorID'].isna(), 'corridorName'].unique()
if 'Rusun Marunda - Terminal Terpadu Pulo Gebang' in corridor_nan:
    df.loc[df['corridorID'].isna(), 'corridorID'] = 'JAK110A'
# Fill missing corridorName
if df['corridorName'].isna().sum() > 0:
    df.loc[df['corridorName'].isna(), 'corridorName'] = 'Rusun Flamboyan-Kalideres'
# Drop rows with missing tapInStops
df = df.loc[df['tapInStops'].notna()]
# Drop rows with missing tapOutStops
df = df.loc[df['tapOutStops'].notna()]
# Fill payAmount
corridor_list = ['1T', 'B14', '3B', 'T21', 'D32', 'S31', 'B13', 'D31', '1K', '6P', 'S12']
df.loc[(df['payCardBirthDate'] <= 1963) & (df['payAmount'].isna()), 'payAmount'] = 0.0
df.loc[df['corridorID'].isin(corridor_list) & df['payAmount'].isna(), 'payAmount'] = 20000.0
df.loc[df['payAmount'].isna(), 'payAmount'] = 3500.0
# Add Age column
df['Age'] = 2023 - df['payCardBirthDate']
df.insert(3, 'Age', df.pop('Age'))
df = df.drop(columns='payCardBirthDate')
# Convert datetime columns
df['tapInTime'] = pd.to_datetime(df['tapInTime'])
df['tapOutTime'] = pd.to_datetime(df['tapOutTime'])
df['tapInTime2'] = df['tapInTime'].dt.strftime('%H:%M')
df['tapInDay'] = df['tapInTime'].dt.strftime('%A')
df['tapInDate'] = df['tapInTime'].dt.strftime('%m-%d')
df.insert(8, 'tapInTime2', df.pop('tapInTime2'))
df.insert(9, 'tapInDay', df.pop('tapInDay'))
df.insert(10, 'tapInDate', df.pop('tapInDate'))
df = df.drop(columns='tapInTime')
df = df.rename(columns={'tapInTime2': 'tapInTime'})
df['tapOutTime2'] = df['tapOutTime'].dt.strftime('%H:%M')
df['tapOutDay'] = df['tapOutTime'].dt.strftime('%A')
df['tapOutDate'] = df['tapOutTime'].dt.strftime('%m-%d')
df.insert(13, 'tapOutTime2', df.pop('tapOutTime2'))
df.insert(14, 'tapOutDay', df.pop('tapOutDay'))
df.insert(15, 'tapOutDate', df.pop('tapOutDate'))
df = df.drop(columns='tapOutTime')
df = df.rename(columns={'tapOutTime2': 'tapOutTime'})

st.subheader("Cleaned Data Preview")
st.dataframe(df.head())

# Data summary
def data_summary(df):
    listItem = []
    for col in df.columns:
        if df[col].nunique() > 2:
            samp = df[col].drop_duplicates().sample(2).values
        else:
            samp = df[col].drop_duplicates().values
        # Convert sample to string for display
        samp_str = [str(x) for x in samp]
        listItem.append([col, str(df[col].dtype), df[col].isna().sum(), df[col].nunique(), ", ".join(samp_str)])
    return pd.DataFrame(columns=['dataFeatures', 'dataType', 'null', 'unique', 'uniqueSample'], data=listItem)

with st.expander("Cleaned Data Summary Table"):
    st.dataframe(data_summary(df))

# Simple Visualization
with st.expander("Simple Visualizations"):
    st.write("Distribution of Age")
    st.bar_chart(df['payCardSex'].value_counts().sort_index())
    st.write("Distribution of payAmount")
    st.bar_chart(df['payAmount'].value_counts().sort_index())
