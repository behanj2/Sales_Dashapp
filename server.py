# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 18:23:15 2024

@author: Joseph.Behan

THis code stores some core server configuarion. Without this server file @calbacks will
not function in a multipage dash app.

"""

import dash
import dash_bootstrap_components as dbc

# Define Rio Tinto color scheme
rio_tinto_colors = {
    'background': '#F3F3F3',
    'text': '#2c2c2c',
    'primary': '#D22630',
    'secondary': '#FFFFFF',
    'accent': '#005792',
    'plot_bg': '#F3F3F3',
    'paper_bg': '#F3F3F3',
    'line': '#D22630',
    'bar': '#005792'
}

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Sales Dashboard"
server = app.server

