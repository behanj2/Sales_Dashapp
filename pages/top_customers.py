# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 07:41:39 2024

@author: Joseph.Behan

Qyuick analysis of the top customers up to 20.

"""
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import pandas as pd
from dash.dependencies import Input, Output
from server import app, rio_tinto_colors
import pySQL_library as hrdb

# Function to create the layout
def create_layout():
    sales_df, customers_df = hrdb.get_data()
    top_customers = sales_df.groupby('CustomerID').sum(numeric_only=True)['TotalAmount'].reset_index()
    top_customers = top_customers.nlargest(10, 'TotalAmount').merge(customers_df, on='CustomerID')

    fig_top_customers = px.bar(
        top_customers,
        x='CustomerID',
        y='TotalAmount',
        title='Top 10 Customers by Sales',
        template='plotly_white',
        color_discrete_sequence=['#005792']
    )

    layout = dbc.Container(
        [
            dbc.Row(
                dbc.Col(html.H2("", className='text-center'), width=12)
            ),
            dbc.Row(
                dbc.Col(
                    html.Div([
                        html.Label('Select Number of Top Customers', style={'marginBottom': '10px'}),
                        dcc.Slider(
                            id='customer-slider',
                            min=1,
                            max=20,
                            step=1,
                            value=10,
                            marks={i: str(i) for i in range(1, 21)},
                            className='mb-4'
                        )
                    ], style={'marginTop': '20px'}),
                    width=12
                )
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id='top-customers-graph', figure=fig_top_customers), width=6),
                    dbc.Col(dcc.Graph(id='sales-percentage-graph'), width=6),
                ]
            ),
            dbc.Row(
                dbc.Col(dcc.Graph(id='clv-bubble-chart', style={"height": "50vh"}), width=12)
            ),
        ],
        fluid=True,
    )
    return layout

# Register the layout function as the page layout
layout = create_layout()

@app.callback(
    [Output('top-customers-graph', 'figure'),
     Output('sales-percentage-graph', 'figure'),
     Output('clv-bubble-chart', 'figure')],
    [Input('customer-slider', 'value')]
)
def update_top_customers(num_customers):
    sales_df, customers_df = hrdb.get_data()
    
    top_customers = sales_df.groupby('CustomerID').sum(numeric_only=True)['TotalAmount'].reset_index()
    top_customers = top_customers.nlargest(num_customers, 'TotalAmount').merge(customers_df, on='CustomerID')

    fig_top_customers = px.bar(
        top_customers,
        x='CustomerID',
        y='TotalAmount',
        title=f'Top {num_customers} Customers by Sales',
        template='plotly_white',
        color_discrete_sequence=['#005792']
    )

    total_sales = sales_df['TotalAmount'].sum()
    percentage_sales = top_customers['TotalAmount'].sum() / total_sales * 100
    remaining_sales = total_sales - top_customers['TotalAmount'].sum()
    
    fig_sales_percentage = go.Figure(go.Pie(
        labels=[f'Top {num_customers} Customers', 'Others'],
        values=[percentage_sales, 100 - percentage_sales],
        marker=dict(colors=['#005792', '#E5E5E5'])
    ))
    fig_sales_percentage.update_layout(title='Sales Percentage by Top Customers')

    clv_summary = sales_df.groupby('CustomerID').agg(
        AverageOrderValue=pd.NamedAgg(column='TotalAmount', aggfunc='mean'),
        PurchaseFrequency=pd.NamedAgg(column='TransactionID', aggfunc='count')
    ).reset_index()

    average_lifespan = 3
    clv_summary['PurchaseFrequency'] = clv_summary['PurchaseFrequency'] / len(sales_df['Date'].dt.year.unique())
    clv_summary['CLV'] = clv_summary['AverageOrderValue'] * clv_summary['PurchaseFrequency'] * average_lifespan

    fig_clv_bubble = px.scatter(
        clv_summary,
        x='AverageOrderValue',
        y='PurchaseFrequency',
        size='CLV',
        color='CLV',
        hover_data=['CustomerID'],
        title='Customer Lifetime Value (CLV) = (Ave Order Value * Purchase Frequency * Average Lifespan)',
        template='plotly_white',
        color_continuous_scale='Viridis',
        height=700  # Increase the height of the plot
    )

    # Add threshold line
    fig_clv_bubble.add_shape(
        type='line',
        x0=clv_summary['AverageOrderValue'].min(),
        y0=750 / clv_summary['AverageOrderValue'].min() / average_lifespan,
        x1=clv_summary['AverageOrderValue'].max(),
        y1=500 / clv_summary['AverageOrderValue'].max() / average_lifespan,
        line=dict(color='red', dash='dash')
    )

    fig_clv_bubble.update_layout(coloraxis_colorbar=dict(title='CLV'))

    return fig_top_customers, fig_sales_percentage, fig_clv_bubble