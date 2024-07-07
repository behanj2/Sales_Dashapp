# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 07:41:39 2024

@author: Joseph.Behan
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('sales_transactions.db')
sales_df = pd.read_sql_query("SELECT * FROM salesdetails", conn)
conn.close()

# Products with the Highest Discounts
highest_discounts = sales_df.groupby('ProductID').sum()['Discount'].reset_index()
highest_discounts = highest_discounts.nlargest(10, 'Discount')
fig_highest_discounts = px.bar(highest_discounts, x='ProductID', y='Discount', title='Products with Highest Discounts', template='plotly_white', color_discrete_sequence=['#005792'])

layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(html.H2("Highest Discounts", className='text-center'), width=12)
        ),
        dbc.Row(
            dbc.Col(dcc.Graph(id='highest-discounts-graph', figure=fig_highest_discounts), width=12)
        ),
    ],
    fluid=True,
)
