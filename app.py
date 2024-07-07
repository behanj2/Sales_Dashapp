# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 07:35:35 2024

@author: Joseph.Behan
"""
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
from server import app, server, rio_tinto_colors
import plotly.express as px
import subprocess

# Import the page layouts
from pages import overview, sales_by_region, top_customers, best_selling_products

# Layout for the header
header = html.Div(
    [
        html.H1("Sales Dashboard", style={"textAlign": "center", "margin": "0", "padding": "20px 0", "color": rio_tinto_colors['text']}),
        html.Button("Refresh Data", id="refresh-button", className="btn btn-primary", style={"position": "absolute", "right": "20px", "top": "20px"})
    ],
    style={"width": "100%", "backgroundColor": rio_tinto_colors['secondary'], "boxShadow": "0px 4px 2px -2px gray", "position": "fixed", "top": "0", "zIndex": "1000"}
)

# Layout for the sidebar
sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink("Overview", href="/overview", active="exact"),
                dbc.NavLink("Sales by Region", href="/sales-by-region", active="exact"),
                dbc.NavLink("Top Customers", href="/top-customers", active="exact"),
                dbc.NavLink("Best Selling Products", href="/best-selling-products", active="exact"),
            ],
            vertical=True,
            pills=True,
            className="bg-light",
            style={"height": "85vh", "backgroundColor": 'ghostwhite'}
        ),
        html.Div(
            html.Img(src="/assets/RT_Primary_Red_RGB.png", style={"width": "100%", "padding": "0x", "backgroundColor": 'ghostwhite'}),
            style={"height": "0vh", "display": "flex", "alignItems": "center", "justifyContent": "center", "backgroundColor": 'ghostwhite'}
        ),
    ],
    style={"width": "20%", "float": "left", "height": "100vh", "paddingTop": "90px", "backgroundColor": rio_tinto_colors['background']}
)

# Main layout
content = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(id="page-content")
    ],
    style={"width": "80%", "float": "right", "height": "100vh", "overflow": "auto", "backgroundColor": 'white', "paddingTop": "80px"}
)

# Define the layout for the app
app.layout = html.Div([header, sidebar, content])

# Callback to handle page routing
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/overview":
        return overview.layout
    elif pathname == "/sales-by-region":
        return sales_by_region.layout
    elif pathname == "/top-customers":
        return top_customers.layout
    elif pathname == "/best-selling-products":
        return best_selling_products.layout
    else:
        return html.H1("404: Page Not Found", className='text-center')

# Callback to handle data refresh
@app.callback(
    Output('refresh-button', 'children'),
    [Input('refresh-button', 'n_clicks')]
)
def refresh_data(n_clicks):
    if n_clicks:
        try:
            # Run the database.py script
            subprocess.run(["python", "database.py"])
            return "Data Refreshed!"
        except Exception as e:
            return f"Error: {e}"
    return "Refresh Data"

if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=8050)



