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
import time

def print_table_contents(db, table_name):
    """Print the contents of a table."""
    print(f"Contents of {table_name} table:")
    cursor = db.execute(f'SELECT * FROM "{table_name}"')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    if not rows:
        print("No data found.")
    print()



def update_database_from_csv(db, customer_csv, sales_csv, max_retries=5):
    """Update the database with new rows from the CSV files."""
    for attempt in range(max_retries):
        try:
            # Update customer details
            with open(customer_csv, newline='') as f:
                reader = csv.DictReader(f)
                customers = {row['CustomerID'] for row in reader}  # Use a set to ensure uniqueness

            existing_customers = {str(row[0]) for row in db.execute('SELECT CustomerID FROM customerdetails')}
            new_customers = customers - existing_customers

            if new_customers:
                insert_sql = 'INSERT OR IGNORE INTO customerdetails (CustomerID) VALUES (?)'
                db.executemany(insert_sql, [(customer,) for customer in new_customers])
                print(f"Inserted {len(new_customers)} new customers into customerdetails table.")
            else:
                print("No new customers to insert.")

            # Update sales details
            with open(sales_csv, newline='') as f:
                reader = csv.DictReader(f)
                sales = [tuple(row[col] for col in reader.fieldnames) for row in reader]
                sales_fieldnames = reader.fieldnames

            existing_sales = {str(row[0]) for row in db.execute('SELECT TransactionID FROM salesdetails')}
            new_sales = [row for row in sales if str(row[sales_fieldnames.index('TransactionID')]) not in existing_sales]

            if new_sales:
                columns = ', '.join(sales_fieldnames)
                placeholders = ', '.join('?' for _ in sales_fieldnames)
                insert_sql = f'INSERT INTO salesdetails ({columns}) VALUES ({placeholders})'
                db.executemany(insert_sql, new_sales)
                print(f"Inserted {len(new_sales)} new transactions into salesdetails table.")
            else:
                print("No new sales transactions to insert.")

            break  # If successful, exit the retry loop
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                print(f"Attempt {attempt + 1} of {max_retries} failed: database is locked. Retrying in 1 second...")
                time.sleep(1)  # Wait before retrying
            else:
                raise
    else:
        print("Failed to update the database after multiple attempts due to database being locked.")









# Connect to the SQLite database and create tables
db_name = 'sales_transactions.db'
customer_csv = 'customer_details.csv'  # Update 'customer_details.csv' to the actual path
sales_csv = 'sales_transactions.csv'  # Update 'sales_transactions.csv' to the actual path


if not os.path.exists(db_name): 
    conn = sqlite3.connect(db_name)
    hrdb.create_customerdetails_table(customer_csv, conn)  # Update 'customer_details.csv' to the actual path
    hrdb.create_salesdetails_table(sales_csv, conn)  # Update 'sales_transactions.csv' to the actual path

    # Print table contents
    print_table_contents(conn, 'customerdetails')
    print_table_contents(conn, 'salesdetails')

    conn.commit()
    conn.close()
else:
    print(f"Database {db_name} already exists.")
    conn = sqlite3.connect(db_name)
    
    # Update the database with new rows from the CSV files
    update_database_from_csv(conn, customer_csv, sales_csv)

    # Apply transformation
    hrdb.transform_data(conn)

    # Print table contents after transformation
    print_table_contents(conn, 'salesdetails')

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



