# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 07:40:49 2024

@author: Joseph.Behan
"""
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import pandas as pd
import json
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
    merged_df = pd.merge(sales_df, customers_df, on='CustomerID')
    
    # Calculate total sales per state
    state_sales = merged_df.groupby('State')['TotalAmount'].sum().reset_index()

    # Load Australian states geojson file
    with open('australia.geojson', 'r') as f:
        geojson = json.load(f)

    # Create the choropleth map figure
    fig_map = px.choropleth(
        state_sales,
        geojson=geojson,
        locations='State',
        featureidkey='properties.STATE_NAME',
        color='TotalAmount',
        hover_name='State',
        hover_data={'TotalAmount': True},
        title='Sales Distribution across Australian States',
        template='plotly_white',
        color_continuous_scale='viridis'
    )

    # Update the layout for better focus on Australia
    fig_map.update_geos(
        projection_type='natural earth',
        showland=True,
        landcolor="white",
        showcountries=True,
        countrycolor="white",
        lataxis=dict(range=[-45, -10]),
        lonaxis=dict(range=[110, 155]),
        showcoastlines=True,
        coastlinecolor="black",
        showocean=True,
        oceancolor="white"
    )

    fig_map.update_layout(
        title_font=dict(size=24, family='Arial, sans-serif', color='black'),
        geo=dict(
            bgcolor='rgba(0,0,0,0)'
        ),
        margin=dict(l=0, r=0, t=50, b=0)
    )

    # Sales Breakdown by Region
    sales_by_region = sales_df.groupby('Region').sum(numeric_only=True)['TotalAmount'].reset_index()

    # Create a diamond layout for regions
    fig_diamond = go.Figure()

    # Define the positions of the corners of the diamond
    corners = {
        'North': (0.5, 1.0),
        'South': (0.5, 0.0),
        'East': (1.0, 0.5),
        'West': (0.0, 0.5)
    }

    # Calculate the sales sum for normalization
    total_sales = sales_by_region['TotalAmount'].sum()
    if total_sales == 0:
        total_sales = 1

    # Create a scatter plot for the regions
    fig_diamond.add_trace(go.Scatter(
        x=[corners[region][0] for region in sales_by_region['Region']],
        y=[corners[region][1] for region in sales_by_region['Region']],
        text=[f"{region}<br>{sales:.2f}" for region, sales in zip(sales_by_region['Region'], sales_by_region['TotalAmount'])],
        mode='markers+text',
        marker=dict(size=5, color='red'),
        textposition='top center'
    ))

    # Calculate the position of the red dot
    weighted_x = sum(corners[region][0] * sales for region, sales in zip(sales_by_region['Region'], sales_by_region['TotalAmount'])) / total_sales
    weighted_y = sum(corners[region][1] * sales for region, sales in zip(sales_by_region['Region'], sales_by_region['TotalAmount'])) / total_sales

    # Add the red dot
    fig_diamond.add_trace(go.Scatter(
        x=[weighted_x],
        y=[weighted_y],
        mode='markers+text',
        marker=dict(size=12, color='red'),
        text=[f"Total: {total_sales:.2f}<br>Date: {sales_df['Date'].max().date()}"],
        textposition='top center'
    ))

    # Add semi-translucent red dots for other points in time
    historical_points = sales_df['Date'].unique()[:-1]  # Exclude the latest date
    viridis_colors = px.colors.sequential.Viridis
    color_scale = [viridis_colors[int(i * (len(viridis_colors) - 1) / (len(historical_points) - 1))] for i in range(len(historical_points))]
    for date, color in zip(historical_points, color_scale):
        filtered_df = sales_df[sales_df['Date'] <= date]
        sales_by_region_hist = filtered_df.groupby('Region').sum(numeric_only=True)['TotalAmount'].reset_index()
        total_sales_hist = sales_by_region_hist['TotalAmount'].sum()
        if total_sales_hist == 0:
            total_sales_hist = 1
        
        def get_percentage(region):
            if region in sales_by_region_hist['Region'].values:
                return f"{sales_by_region_hist[sales_by_region_hist['Region'] == region]['TotalAmount'].values[0] / total_sales_hist:.2%}"
            else:
                return 'N/A'

        weighted_x_hist = sum(corners[region][0] * sales for region, sales in zip(sales_by_region_hist['Region'], sales_by_region_hist['TotalAmount'])) / total_sales_hist
        weighted_y_hist = sum(corners[region][1] * sales for region, sales in zip(sales_by_region_hist['Region'], sales_by_region_hist['TotalAmount'])) / total_sales_hist
        fig_diamond.add_trace(go.Scatter(
            x=[weighted_x_hist],
            y=[weighted_y_hist],
            mode='markers',
            marker=dict(size=10, color=color, opacity=0.5),
            text=[f"Date: {date.date()}<br>East: {get_percentage('East')}<br>West: {get_percentage('West')}<br>North: {get_percentage('North')}<br>South: {get_percentage('South')}"]
        ))

    # Add the grid lines
    fig_diamond.add_shape(type="line",
        x0=0.5, y0=0.0, x1=0.5, y1=1.0,
        line=dict(color="black", width=2)
    )
    fig_diamond.add_shape(type="line",
        x0=0.0, y0=0.5, x1=1.0, y1=0.5,
        line=dict(color="black", width=2)
    )
    fig_diamond.add_shape(type="line",
        x0=0.0, y0=0.5, x1=0.5, y1=1.0,
        line=dict(color="black", width=2)
    )
    fig_diamond.add_shape(type="line",
        x0=0.5, y0=1.0, x1=1.0, y1=0.5,
        line=dict(color="black", width=2)
    )
    fig_diamond.add_shape(type="line",
        x0=1.0, y0=0.5, x1=0.5, y1=0.0,
        line=dict(color="black", width=2)
    )
    fig_diamond.add_shape(type="line",
        x0=0.5, y0=0.0, x1=0.0, y1=0.5,
        line=dict(color="black", width=2)
    )

    fig_diamond.update_layout(
        title='Sales by Region',
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.1, 1.1]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.1, 1.1]),
        template='plotly_white',
        height=600,
        coloraxis=dict(colorscale='Viridis', colorbar=dict(title='Date', ticks='outside'))
    )

    layout = dbc.Container(
        [
            dbc.Row(
                dbc.Col(html.H2("", className='text-center', style={"paddingTop": "30px"}), width=12)
            ),
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
                                style={"marginBottom": "10px"}
                            )
                        ], style={"textAlign": "center"}),
                        width={"size": 6, "offset": 3}
                    ),
                ],
                className="mb-4",
                style={"height": "15vh"}
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(id='diamond-graph', figure=fig_diamond),
                        width=6
                    ),
                    dbc.Col(
                        dcc.Graph(id='sales-map', figure=fig_map),
                        width=6
                    ),
                ],
                className="mb-4"
            ),
        ],
        fluid=True,
        style={"height": "100vh"}
    )
    return layout

# Register the layout function as the page layout
layout = create_layout()

@app.callback(
    [Output('diamond-graph', 'figure'),
     Output('sales-map', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(start_date, end_date):
    sales_df, customers_df = get_data()
    merged_df = pd.merge(sales_df, customers_df, on='CustomerID')

    # Define the positions of the corners of the diamond
    corners = {
        'North': (0.5, 1.0),
        'South': (0.5, 0.0),
        'East': (1.0, 0.5),
        'West': (0.0, 0.5)
    }

    # Ensure dates are in datetime format
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the data based on the selected date range
    filtered_df = sales_df[(sales_df['Date'] >= start_date) & (sales_df['Date'] <= end_date)]
    sales_by_region = filtered_df.groupby('Region').sum(numeric_only=True)['TotalAmount'].reset_index()
    state_sales = merged_df[merged_df['Date'].between(start_date, end_date)].groupby('State')['TotalAmount'].sum().reset_index()

    # Calculate the sales sum for normalization
    total_sales = sales_by_region['TotalAmount'].sum()
    if total_sales == 0:
        total_sales = 1

    # Create a diamond layout for regions
    fig_diamond = go.Figure()

    # Create a scatter plot for the regions
    fig_diamond.add_trace(go.Scatter(
        x=[corners[region][0] for region in sales_by_region['Region']],
        y=[corners[region][1] for region in sales_by_region['Region']],
        text=[f"{region}<br>{sales:.2f}" for region, sales in zip(sales_by_region['Region'], sales_by_region['TotalAmount'])],
        mode='markers+text',
        marker=dict(size=10, color='black'),
        textposition='top center'
    ))

    # Calculate the position of the red dot
    weighted_x = sum(corners[region][0] * sales for region, sales in zip(sales_by_region['Region'], sales_by_region['TotalAmount'])) / total_sales
    weighted_y = sum(corners[region][1] * sales for region, sales in zip(sales_by_region['Region'], sales_by_region['TotalAmount'])) / total_sales

    # Add the red dot
    fig_diamond.add_trace(go.Scatter(
        x=[weighted_x],
        y=[weighted_y],
        mode='markers+text',
        marker=dict(size=12, color='red'),
        text=[f"Total: {total_sales:.2f}<br>Date: {end_date.date()}"],
        textposition='top center'
    ))

    # Add semi-translucent red dots for other points in time
    historical_points = filtered_df['Date'].unique()[:-1]  # Exclude the latest date
    viridis_colors = px.colors.sequential.Viridis
    color_scale = [viridis_colors[int(i * (len(viridis_colors) - 1) / (len(historical_points) - 1))] for i in range(len(historical_points))]
    for date, color in zip(historical_points, color_scale):
        hist_filtered_df = filtered_df[filtered_df['Date'] <= date]
        sales_by_region_hist = hist_filtered_df.groupby('Region').sum(numeric_only=True)['TotalAmount'].reset_index()
        total_sales_hist = sales_by_region_hist['TotalAmount'].sum()
        if total_sales_hist == 0:
            total_sales_hist = 1
        
        def get_percentage(region):
            if region in sales_by_region_hist['Region'].values:
                return f"{sales_by_region_hist[sales_by_region_hist['Region'] == region]['TotalAmount'].values[0] / total_sales_hist:.2%}"
            else:
                return 'N/A'

        weighted_x_hist = sum(corners[region][0] * sales for region, sales in zip(sales_by_region_hist['Region'], sales_by_region_hist['TotalAmount'])) / total_sales_hist
        weighted_y_hist = sum(corners[region][1] * sales for region, sales in zip(sales_by_region_hist['Region'], sales_by_region_hist['TotalAmount'])) / total_sales_hist
        fig_diamond.add_trace(go.Scatter(
            x=[weighted_x_hist],
            y=[weighted_y_hist],
            mode='markers',
            marker=dict(size=10, color=color, opacity=0.5),
            text=[f"Date: {date.date()}<br>East: {get_percentage('East')}<br>West: {get_percentage('West')}<br>North: {get_percentage('North')}<br>South: {get_percentage('South')}"]
        ))

    # Add the grid lines
    fig_diamond.add_shape(type="line",
        x0=0.5, y0=0.0, x1=0.5, y1=1.0,
        line=dict(color="black", width=2)
    )
    fig_diamond.add_shape(type="line",
        x0=0.0, y0=0.5, x1=1.0, y1=0.5,
        line=dict(color="black", width=2)
    )
    fig_diamond.add_shape(type="line",
        x0=0.0, y0=0.5, x1=0.5, y1=1.0,
        line=dict(color="black", width=2)
    )
    fig_diamond.add_shape(type="line",
        x0=0.5, y0=1.0, x1=1.0, y1=0.5,
        line=dict(color="black", width=2)
    )
    fig_diamond.add_shape(type="line",
        x0=1.0, y0=0.5, x1=0.5, y1=0.0,
        line=dict(color="black", width=2)
    )
    fig_diamond.add_shape(type="line",
        x0=0.5, y0=0.0, x1=0.0, y1=0.5,
        line=dict(color="black", width=2)
    )

    fig_diamond.update_layout(
        title='Temporal Map of Sales by Region',
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.1, 1.1]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.1, 1.1]),
        template='plotly_white',
        height=600,
        coloraxis=dict(colorscale='Viridis', colorbar=dict(title='Date', ticks='outside'))
    )

    # Create the choropleth map figure
    with open('australia.geojson', 'r') as f:
        geojson = json.load(f)

    fig_map = px.choropleth(
        state_sales,
        geojson=geojson,
        locations='State',
        featureidkey='properties.STATE_NAME',
        color='TotalAmount',
        hover_name='State',
        hover_data={'TotalAmount': True},
        title='Sales Distribution across Australian States',
        template='plotly_white',
        color_continuous_scale='viridis'
    )

    fig_map.update_geos(
        projection_type='natural earth',
        showland=True,
        landcolor="white",
        showcountries=True,
        countrycolor="white",
        lataxis=dict(range=[-45, -10]),
        lonaxis=dict(range=[110, 155]),
        showcoastlines=True,
        coastlinecolor="black",
        showocean=True,
        oceancolor="white"
    )

    fig_map.update_layout(
        title_font=dict(size=24, family='Arial, sans-serif', color='black'),
        geo=dict(
            bgcolor='rgba(0,0,0,0)'
        ),
        margin=dict(l=0, r=0, t=50, b=0)
    )

    return fig_diamond, fig_map

layout = create_layout()




