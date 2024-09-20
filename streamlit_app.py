import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import datetime

import streamlit as st

from Inflation_impact import country_inflation, stock_quote_year_price, price_inflation_adjusted 
#country_inflation(code), stock_quote_year_price(ticker), price_inflation_adjusted(ticker, code)

##########################################################################################################
#######################################Querys#############################################################
###############Stock Market########################
conn1 = sqlite3.connect('StockMarket.db')
cursor1 = conn1.cursor()

cursor1.execute("SELECT ticker, name FROM Companies")
companies = cursor1.fetchall()

conn1.close()

###############Inflation########################
conn2 = sqlite3.connect('Inflation.db')
cursor2 = conn2.cursor()

cursor2.execute("SELECT name, code FROM Countries")
countries = cursor2.fetchall()

conn2.close()

##########################################################################################################

st.markdown("<h1 style='text-align: center; color: skyblue;'>Inflación y su impacto en la bolsa</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<p style='font-size: 17px; color: whitebone;'>&nbsp;&nbsp;&nbsp; La <strong>inflación</strong> es el aumento generalizado y sostenido de los precios existentes en el mercado durante un período de tiempo, generalmente un año.</p>", unsafe_allow_html=True)
st.markdown("<br><br><br>", unsafe_allow_html=True)

st.title("Stocks available")
company_selected = st.selectbox("Selecciona el ticker", companies)
stock_quote_year_price(company_selected[0])

st.title("Countries available")
country_selected = st.selectbox("Selecciona el país", countries, index=143)
country_inflation(country_selected[1])

st.title("Inflation adjusted price")
df = price_inflation_adjusted(company_selected[0], country_selected[1])


plt.figure(figsize=(25, 5))

#graphing
plt.plot(df['year'], df['price'], label='Close')
plt.plot(df['year'], df['last_price_adj_inflation'], label='Last price with inflation adjusted')
plt.plot(df['year'], df['real_price_adj'], label='Real price adjusted')

plt.title("Actual price vs Last price with inflation vs Real price adjusted")
plt.xlabel("Year")
plt.ylabel("Price")
plt.legend()
st.pyplot(plt)

st.dataframe(df)

