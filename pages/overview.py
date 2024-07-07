# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 07:37:44 2024

@author: Joseph.Behan
"""
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
import sqlite3
import pandas as pd
from dash.dependencies import Input, Output
from server import app, rio_tinto_colors

# Function to get the data
def get_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('sales_transactions.db')
    sales_df = pd.read_sql_query("SELECT * FROM salesdetails", conn)
    customers_df = pd.read_sql_query("SELECT * FROM customerdetails", conn)
    conn.close()
    # Convert 'Date' column to datetime
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    return sales_df, customers_df

# Function to create the layout
def create_layout():
    sales_df, customers_df = get_data()

    total_sales = sales_df['TotalAmount'].sum()
    total_customers = sales_df['CustomerID'].nunique()
    total_products_sold = sales_df['Quantity'].sum()
    average_order_value = total_sales / sales_df['TransactionID'].nunique()

    # Sales Over Time
    sales_over_time = sales_df.groupby('Date').sum()['TotalAmount'].reset_index()
    fig_sales_over_time = px.line(sales_over_time, x='Date', y='TotalAmount', title='Sales Over Time', template='plotly_white', color_discrete_sequence=[rio_tinto_colors['line']])

    layout = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div([
                            html.H4("Filter by Time Frame", className='text-center'),
                            dcc.DatePickerRange(
                                id='date-picker-range',
                                start_date=sales_df['Date'].min().date(),
                                end_date=sales_df['Date'].max().date(),
                                display_format='YYYY-MM-DD',
                                style={"marginBottom": "10px", "textAlign": "center"}
                            ),
                        ], style={"textAlign": "center"}),
                        width=6,
                    ),
                    dbc.Col(
                        html.Div([
                            html.H4("Filter by Region", className='text-center'),
                            dcc.Checklist(
                                id='region-filter',
                                options=[{'label': region, 'value': region} for region in sales_df['Region'].unique()],
                                value=sales_df['Region'].unique(),
                                inline=True,
                                labelStyle={"margin": "10px"},
                                style={"textAlign": "center"}
                            )
                        ], style={"textAlign": "center"}),
                        width=6,
                    ),
                ],
                className="mb-4",
                style={"height": "15vh"}
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Total Sales", className="card-title text-center", style={"fontSize": "20px"}),
                                    html.P(id="total-sales-card", className="card-text text-center", style={"fontSize": "24px"}),
                                ]
                            ),
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Total Customers", className="card-title text-center", style={"fontSize": "20px"}),
                                    html.P(id="total-customers-card", className="card-text text-center", style={"fontSize": "24px"}),
                                ]
                            ),
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Total Products Sold", className="card-title text-center", style={"fontSize": "20px"}),
                                    html.P(id="total-products-sold-card", className="card-text text-center", style={"fontSize": "24px"}),
                                ]
                            ),
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Average Order Value", className="card-title text-center", style={"fontSize": "20px"}),
                                    html.P(id="average-order-value-card", className="card-text text-center", style={"fontSize": "24px"}),
                                ]
                            ),
                        ),
                        width=3,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                dbc.Col(html.H2("Overview", className='text-center', style={"paddingTop": "20px"}), width=12)
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(id='sales-over-time-graph', figure=fig_sales_over_time),
                        width=12
                    ),
                ],
                className="mb-4",
                style={"height": "30vh"}
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(id='customer-histogram'),
                        width=6
                    ),
                    dbc.Col(
                        dcc.Graph(id='product-histogram'),
                        width=6
                    ),
                ],
                style={"height": "40vh"}
            ),
        ],
        style={"height": "100vh", "padding": "10px"}
    )
    return layout

# Register the layout function as the page layout
layout = create_layout()

@app.callback(
    [Output('customer-histogram', 'figure'),
     Output('product-histogram', 'figure'),
     Output('sales-over-time-graph', 'figure'),
     Output('total-sales-card', 'children'),
     Output('total-customers-card', 'children'),
     Output('total-products-sold-card', 'children'),
     Output('average-order-value-card', 'children')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('region-filter', 'value')]
)
def update_graphs_and_cards(start_date, end_date, selected_regions):
    sales_df, _ = get_data()

    # Check if the dates are properly parsed
    if not start_date or not end_date:
        return {}, {}, {}, "", "", "", ""

    # Ensure dates are in datetime format
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter by date range
    filtered_df = sales_df[(sales_df['Date'] >= start_date) & (sales_df['Date'] <= end_date)]

    # Filter by selected regions
    if selected_regions:
        filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]

    if filtered_df.empty:
        return {}, {}, {}, "", "", "", ""

    total_sales = filtered_df['TotalAmount'].sum()
    total_customers = filtered_df['CustomerID'].nunique()
    total_products_sold = filtered_df['Quantity'].sum()
    average_order_value = total_sales / filtered_df['TransactionID'].nunique()

    customer_histogram = px.histogram(
        filtered_df,
        x='TotalAmount',
        color='CustomerID',
        title='Sales Distribution by Customer',
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Set1
    )

    product_histogram = px.histogram(
        filtered_df,
        x='TotalAmount',
        color='ProductID',
        title='Sales Distribution by Product',
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Set1
    )

    sales_over_time = filtered_df.groupby('Date').sum()['TotalAmount'].reset_index()
    fig_sales_over_time = px.line(sales_over_time, x='Date', y='TotalAmount', title='Sales Over Time', template='plotly_white', color_discrete_sequence=[rio_tinto_colors['line']])

    return (
        customer_histogram, 
        product_histogram, 
        fig_sales_over_time, 
        html.P(f"${total_sales:,.2f}", className="card-text text-center", style={"fontSize": "24px"}), 
        html.P(total_customers, className="card-text text-center", style={"fontSize": "24px"}), 
        html.P(total_products_sold, className="card-text text-center", style={"fontSize": "24px"}), 
        html.P(f"${average_order_value:,.2f}", className="card-text text-center", style={"fontSize": "24px"})
    )

layout = create_layout()








