# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 07:41:39 2024

@author: Joseph.Behan


Qyuick analysis of the top products up to 20.

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

# Function to create the page layout layout
def create_product_layout():
    sales_df, customers_df = hrdb.get_data()
    top_products = sales_df.groupby('ProductID').sum(numeric_only=True)['TotalAmount'].reset_index()
    top_products = top_products.nlargest(10, 'TotalAmount')

    fig_top_products = px.bar(
        top_products,
        x='ProductID',
        y='TotalAmount',
        title='Top 10 Products by Sales',
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
                        html.Label('Select Number of Products', style={'marginBottom': '10px'}),
                        dcc.Slider(
                            id='product-slider',
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
                    dbc.Col(dcc.Graph(id='top-products-graph', figure=fig_top_products), width=6),
                    dbc.Col(dcc.Graph(id='product-sales-percentage-graph'), width=6),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id='plv-bubble-chart', style={"height": "50vh"}), width=6),
                    dbc.Col(dcc.Graph(id='highest-discounts-graph', style={"height": "50vh"}), width=6),
                ]
            ),
        ],
        fluid=True,
    )
    return layout

# Register the layout function as the page layout
product_layout = create_product_layout()

@app.callback(
    [Output('top-products-graph', 'figure'),
     Output('product-sales-percentage-graph', 'figure'),
     Output('plv-bubble-chart', 'figure'),
     Output('highest-discounts-graph', 'figure')],
    [Input('product-slider', 'value')]
)
def update_top_products(num_products):
    sales_df, customers_df = hrdb.get_data()
    
    top_products = sales_df.groupby('ProductID').sum(numeric_only=True)['TotalAmount'].reset_index()
    top_products = top_products.nlargest(num_products, 'TotalAmount')

    fig_top_products = px.bar(
        top_products,
        x='ProductID',
        y='TotalAmount',
        title=f'Top {num_products} Products by Sales',
        template='plotly_white',
        color_discrete_sequence=['#005792']
    )

    total_sales = sales_df['TotalAmount'].sum()
    percentage_sales = top_products['TotalAmount'].sum() / total_sales * 100
    remaining_sales = total_sales - top_products['TotalAmount'].sum()
    
    fig_sales_percentage = go.Figure(go.Pie(
        labels=[f'Top {num_products} Products', 'Others'],
        values=[percentage_sales, 100 - percentage_sales],
        marker=dict(colors=['#005792', '#E5E5E5'])
    ))
    fig_sales_percentage.update_layout(title='Sales Percentage by Top Products')

    plv_summary = sales_df.groupby('ProductID').agg(
        AverageOrderValue=pd.NamedAgg(column='TotalAmount', aggfunc='mean'),
        PurchaseFrequency=pd.NamedAgg(column='TransactionID', aggfunc='count')
    ).reset_index()

    average_lifespan = 3  # Adjust as needed
    plv_summary['PurchaseFrequency'] = plv_summary['PurchaseFrequency'] / len(sales_df['Date'].dt.year.unique())
    plv_summary['PLV'] = plv_summary['AverageOrderValue'] * plv_summary['PurchaseFrequency'] * average_lifespan

    fig_plv_bubble = px.scatter(
        plv_summary,
        x='AverageOrderValue',
        y='PurchaseFrequency',
        size='PLV',
        color='PLV',
        hover_data=['ProductID'],
        title='Product Lifetime Value (PLV)',
        template='plotly_white',
        color_continuous_scale='Viridis'
    )

    # Add threshold line
    fig_plv_bubble.add_shape(
        type='line',
        x0=plv_summary['AverageOrderValue'].min(),
        y0=500 / plv_summary['AverageOrderValue'].min() / average_lifespan,
        x1=plv_summary['AverageOrderValue'].max(),
        y1=500 / plv_summary['AverageOrderValue'].max() / average_lifespan,
        line=dict(color='red', dash='dash')
    )

    fig_plv_bubble.update_layout(coloraxis_colorbar=dict(title='PLV'))

    # Products with Highest Discounts
    discount_summary = sales_df.groupby('ProductID').agg(
        AverageDiscount=pd.NamedAgg(column='Discount', aggfunc='mean'),
        TotalAmount=pd.NamedAgg(column='TotalAmount', aggfunc='sum')
    ).reset_index()

    top_discounts = discount_summary.nlargest(num_products, 'AverageDiscount')

    fig_highest_discounts = px.scatter(
        top_discounts,
        x='ProductID',
        y='AverageDiscount',
        size='AverageDiscount',
        color='TotalAmount',
        hover_data=['ProductID'],
        title='Products with Highest Discounts',
        template='plotly_white',
        color_continuous_scale='Viridis'
    )

    return fig_top_products, fig_sales_percentage, fig_plv_bubble, fig_highest_discounts

layout = product_layout


