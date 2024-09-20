#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import datetime

import requests


# In[2]:


url_inflation_db = "https://github.com/matublaq/DataBases/raw/main/Inflation.db"
local_path = "Inflation.db"

response = requests.get(url_inflation_db)

if(response.status_code == 200):
    with open(local_path, 'wb') as file:
        file.write(response.content)
    print(f"Inflation database. Downloaded successfully. Status code {response.status_code}")
else:
    print(f"Inflation database. Download failed. Status code {response.status_code}")

################################################################################################################

url_stockmarket_db = "https://github.com/matublaq/DataBases/raw/main/StockMarket.db"
local_path = "StockMarket.db"

response = requests.get(url_stockmarket_db)

if(response.status_code == 200):
    with open(local_path, 'wb') as file:
        file.write(response.content)
    print(f"Stock market database. Downloaded successfully. Status code {response.status_code}")
else:
    print(f"Stock market database. Download failed. Status code {response.status_code}")


# In[3]:


conn1 = sqlite3.connect('Inflation.db')
conn2 = sqlite3.connect('StockMarket.db')
cursor1 = conn1.cursor()
cursor2 = conn2.cursor()


cursor1.execute("SELECT name FROM Countries")
countries = cursor1.fetchall()
countries = [country[0] for country in countries]

cursor2.execute("SELECT name FROM Companies")
companies = cursor2.fetchall()
companies = [company[0] for company in companies]


conn1.close()
conn2.close()

print(countries, "\n", companies)


# <p style='font-size: 35px; text-align: center; color: violet;'>Functions</p>

# In[4]:


def country_inflation(code):
    conn = sqlite3.connect('Inflation.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM Countries WHERE code = ?", (code,))
    id_country = cursor.fetchall()[0]
    cursor.execute("SELECT year, inflation_rate FROM Inflation WHERE country_id = ?", id_country)
    inflation = cursor.fetchall()

    conn.close()

    return pd.DataFrame(inflation, columns=['year', 'inflation_rate'])

def stock_quote_year_price(ticker):
    with sqlite3.connect('StockMarket.db') as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM Companies WHERE ticker = ?", (ticker,))
        id_company = cursor.fetchall()[0]

        #Last price of every year
        cursor.execute('''
                    SELECT strftime('%Y', date) as year, MAX(date) as max_date, close as price, volume
                    FROM Stock_quotes
                    WHERE company_id = ?
                    GROUP BY year
        ''', id_company)
        company_stock_year = cursor.fetchall()
        company_stock_year = pd.DataFrame(company_stock_year, columns=['year', 'max_date', 'price', 'volume'])
        company_stock_year.drop(columns=['max_date'], inplace=True)
        return company_stock_year

def price_inflation_adjusted(ticker, country_code):
    prices = stock_quote_year_price(ticker)
    inflations = country_inflation(country_code)
    prices['GROWTH'] = 0
    prices['real_price_adj'] = 0
    prices['inflation'] = 0
    prices['last_price_adj_inflation'] = 0

    today = datetime.datetime.now()
    for year in prices['year']:
        if year == str(today.year):
            prices.loc[prices['year'] == year, 'real_price_adj'] = prices.loc[prices['year'] == year, 'price']
            prices.loc[prices['year'] == year, 'inflation'] = prices.loc[prices['year'] == year, 'price']
            prices.loc[prices['year'] == year, 'last_price_adj_inflation'] = prices.loc[prices['year'] == year, 'price']
            return prices[['year', 'inflation', 'price', 'last_price_adj_inflation', 'real_price_adj', 'GROWTH']]
        
        inflation = inflations[inflations['year'] == int(year)]['inflation_rate'].values[0]
    
        if str(int(year)-1) in prices['year'].values:
            last_price = prices[prices['year'] == str(int(year)-1)]['price'].values[0]
            last_price_adj_inflation = last_price*((inflation/100) + 1)
            actual_price = prices[prices['year'] == year]['price'].values[0]
            
            diff_adj_actual = ((actual_price - last_price_adj_inflation)/last_price_adj_inflation)*100 #Creció o decreció.
            prices.loc[prices['year'] == year, 'GROWTH'] = diff_adj_actual.round(2)
            real_actual_price = last_price*((diff_adj_actual/100) + 1)
                         
            prices.loc[prices['year'] == year, 'real_price_adj'] = real_actual_price.round(3)
            prices.loc[prices['year'] == year, 'inflation'] = inflation
            prices.loc[prices['year'] == year, 'last_price_adj_inflation'] = last_price_adj_inflation.round(3)
        else:
            prices.loc[prices['year'] == year, 'real_price_adj'] = 0
            prices.loc[prices['year'] == year, 'inflation'] = 0
            prices.loc[prices['year'] == year, 'last_price_adj_inflation'] = 0

    return prices[['year', 'inflation', 'price', 'last_price_adj_inflation', 'real_price_adj', 'GROWTH']]


# In[5]:


price_inflation_adjusted('AAPL', 'USA')


# In[6]:


inflations = country_inflation('USA')
inflations


# In[7]:


prices = stock_quote_year_price('AAPL')
prices.columns


# In[8]:


prices_inflation = price_inflation_adjusted('MSFT', 'USA')
prices_inflation


# <p style="font-size: 25px; text-align: center;">Consultas generales</p>

# In[9]:


conn = sqlite3.connect('Inflation.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM Countries WHERE code = 'USA'")
usa = cursor.fetchall()[0]

conn.close()

print(usa)


# In[ ]:




