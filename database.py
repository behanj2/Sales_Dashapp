# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 14:34:20 2024

@author: Joseph.Behan


"""

import csv
import sqlite3
import glob
import os
import pySQL_library as hrdb
import pandas as pd
import time
import requests
import os



db_name = 'data/sales_transactions.db'
customer_csv = 'data/customer_details.csv'
sales_csv = 'data/sales_transactions.csv'


###############################################################################

# This section is placed to allow for downloading directly from Ravi's address.
# In the real world, I would do a check of the data, and just download new data.


customer_csv_url = 'https://github.com/Ravi-Pratap/InsightsDevRole-challenge/blob/98427b5e4ef438d96d6b988d7068e151fa7d94cf/customer_details.csv'  # Update 'customer_details.csv' to the actual path
sales_csv_url = 'https://github.com/Ravi-Pratap/InsightsDevRole-challenge/blob/98427b5e4ef438d96d6b988d7068e151fa7d94cf/sales_transactions.csv'  # Update 'sales_transactions.csv' to the actual path


def url_exists(url):
    try:
        response = requests.head(url, verify=False)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error checking URL {url}: {e}")
        return False

def download_file(url, local_filename):
    # Check if the URL exists
    if not url_exists(url):
        print(f"URL {url} does not exist or is not accessible. Skipping download.")
        return None
    
    # Download the file if the URL is accessible
    with requests.get(url, stream=True, verify=False) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    print(f"Downloaded {local_filename} from {url}.")
    return local_filename

# Download the files
download_file(customer_csv_url, customer_csv)
download_file(sales_csv_url, sales_csv)



###############################################################################

# ETL and Update

###############################################################################
if not os.path.exists(db_name): 
    # Extract data from csv into sql tables

    conn = sqlite3.connect(db_name)
    hrdb.create_customerdetails_table(customer_csv, conn)  # Update 'customer_details.csv' to the actual path
    hrdb.create_salesdetails_table(sales_csv, conn)  # Update 'sales_transactions.csv' to the actual path
    
    # Apply Transformation
    hrdb.transform_data(conn)

    # Print table contents
    hrdb.print_table_contents(conn, 'customerdetails')
    hrdb.print_table_contents(conn, 'salesdetails')

    conn.commit()
    conn.close()
else:
    print(f"Database {db_name} already exists.")
    conn = sqlite3.connect(db_name)
    
    # Update the database with new rows from the CSV files
    hrdb.update_database_from_csv(conn, customer_csv, sales_csv)

    # Apply transformation
    hrdb.transform_data(conn)

    # Print table contents after transformation
    hrdb.print_table_contents(conn, 'salesdetails')

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



