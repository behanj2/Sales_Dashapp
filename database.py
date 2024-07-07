# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 14:34:20 2024

@author: Joseph.Behan


"""

import csv
import sqlite3
import glob
import os
import HR_Library as hrdb
import pandas as pd


# Connect to the SQLite database and create tables
db_name = 'sales_transactions.db'
if not os.path.exists(db_name): 
    conn = sqlite3.connect(db_name)
    hrdb.create_customerdetails_table('sales_transactions.csv', conn)  # Update 'path_to_sales_transactions_csv' to the actual path
    hrdb.create_salesdetails_table('sales_transactions.csv', conn)  # Update 'path_to_sales_transactions_csv' to the actual path
    conn.commit()
    conn.close()



conn = sqlite3.connect(db_name)
# Data Transformation
hrdb.transform_data(conn)
conn.commit()
conn.close()

# Data Loading and Verification
transformed_data = hrdb.query_database("SELECT * FROM salesdetails LIMIT 10")
print("Transformed Data (First 10 Rows):")
print(transformed_data)












"""

1 - Extract all sales data for the last quarter.

"""

sales_last_quarter = hrdb.extract_sales_last_quarter()


print("Sales Data for the Last Quarter:")
print(sales_last_quarter)


"""

2 - Calculate the total sales amount per region.

"""

total_sales_per_region = hrdb.calculate_total_sales_per_region()
print("\nTotal Sales Amount per Region:")
print(total_sales_per_region)

"""

3 - Join the sales data with a customer details table to find the total sales amount per customer.

"""

total_sales_per_customer_df = hrdb.total_sales_per_customer()
print("\nTotal Sales Amount per Customer:")
print(total_sales_per_customer_df)

"""

4- Retrieve the top 10 products by sales amount in the last month.

"""

top_10_products_last_month = hrdb.top_10_products_last_month()
print(top_10_products_last_month)


"""

5 - Identify customers who have not made a purchase in the last six months using a subquery.

"""

customers_no_purchase_last_six_months = hrdb.customers_no_purchase_last_six_months()
print(customers_no_purchase_last_six_months)



