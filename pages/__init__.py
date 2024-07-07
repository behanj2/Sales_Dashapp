# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 07:41:39 2024

@author: Joseph.Behan
"""

# pages/__init__.py
from .overview import layout as overview_layout
from .sales_trends import layout as sales_trends_layout
from .sales_by_region import layout as sales_by_region_layout
from .top_customers import layout as top_customers_layout
from .best_selling_products import layout as best_selling_products_layout
from .highest_discounts import layout as highest_discounts_layout

__all__ = [
    'overview_layout',
    'sales_trends_layout',
    'sales_by_region_layout',
    'top_customers_layout',
    'best_selling_products_layout',
    'highest_discounts_layout'
]


