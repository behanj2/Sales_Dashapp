# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 07:39:33 2024

@author: Joseph.Behan
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import pandas as pd

# Function to get the data
def get_data():
    conn = sqlite3.connect('sales_transactions.db')
    sales_df = pd.read_sql_query("SELECT * FROM salesdetails", conn)
    customers_df = pd.read_sql_query("SELECT * FROM customerdetails", conn)
    conn.close()
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    return sales_df, customers_df

# Connect to the SQLite database and get the data
sales_df, customers_df = get_data()

# Define customer segments based on total amount spent
customer_spending = sales_df.groupby('CustomerID').sum(numeric_only=True)['TotalAmount'].reset_index()
customer_spending['Segment'] = pd.qcut(customer_spending['TotalAmount'], 3, labels=['Low', 'Medium', 'High'])

# Merge the segments back to the sales_df
sales_df = sales_df.merge(customer_spending[['CustomerID', 'Segment']], on='CustomerID', how='left')

# Sales Trends Over Time
sales_trends = sales_df.groupby('Date').sum(numeric_only=True)['TotalAmount'].reset_index()
fig_trends = px.line(sales_trends, x='Date', y='TotalAmount', title='Sales Trends Over Time', template='plotly_white', color_discrete_sequence=['#D22630'])

# Sales Trends by Customer Segment
sales_segment_trends = sales_df.groupby(['Date', 'Segment']).sum(numeric_only=True)['TotalAmount'].reset_index()
fig_segment_trends = px.line(sales_segment_trends, x='Date', y='TotalAmount', color='Segment', title='Sales Trends by Customer Segment', template='plotly_white')

layout = html.Div(
    [
        dbc.Row(
            dbc.Col(html.H2("Sales Trends", className='text-center'), width=12)
        ),
        dbc.Row(
            dbc.Col(dcc.Graph(id='sales-trends-graph', figure=fig_trends), width=12)
        ),
        dbc.Row(
            dbc.Col(dcc.Graph(id='sales-segment-trends-graph', figure=fig_segment_trends), width=12)
        ),
    ],
    style={"height": "100vh", "padding": "10px"}
)



