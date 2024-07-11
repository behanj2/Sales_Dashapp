# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 14:16:15 2024

@author: Joseph.Behan
"""

import csv
import sqlite3
import glob
import os
import pandas as pd
from datetime import datetime, timedelta
import time




###############################################################################

#################### Create the tables within the database ####################

###############################################################################
def create_customerdetails_table(filename, db):
    """Create the customerdetails table in the database from a CSV file."""
    print(f"Creating customerdetails table from {filename}...")
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        table_name = 'customerdetails'
        
        # Drop table if it exists
        db.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        
        # Create table with all required columns
        db.execute(f'''
            CREATE TABLE "{table_name}" (
                "CustomerID" INTEGER PRIMARY KEY,
                "CustomerName" TEXT,
                "City" TEXT,
                "State" TEXT,
                "Postcode" TEXT
            )
        ''')
        
        # Insert data
        insert_sql = f'''
            INSERT INTO "{table_name}" 
            ("CustomerID", "CustomerName", "City", "State", "Postcode") 
            VALUES (?, ?, ?, ?, ?)
        '''
        data = [(int(row['CustomerID']), row['CustomerName'], row['City'], row['State'], row['Postcode']) 
                for row in reader if row['CustomerID'].isdigit()]
        db.executemany(insert_sql, data)
    print(f"customerdetails table created with {len(data)} records.")



def create_salesdetails_table(filename, db):
    """Create the salesdetails table in the database from a CSV file."""
    print(f"Creating salesdetails table from {filename}...")
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        table_name = 'salesdetails'

        # Drop table if it exists
        db.execute(f'DROP TABLE IF EXISTS "{table_name}"')

        # Define columns with appropriate data types
        columns_with_types = []
        for col in columns:
            if col == 'CustomerID':
                continue  # Skip CustomerID
            if col in ['TransactionID', 'ProductID', 'StoreID', 'SalespersonID']:
                columns_with_types.append(f'"{col}" INTEGER')
            elif col == 'Date':
                columns_with_types.append(f'"{col}" DATE')
            elif col == 'Quantity':
                columns_with_types.append(f'"{col}" INTEGER')
            elif col in ['Price', 'Discount', 'TotalAmount']:
                columns_with_types.append(f'"{col}" REAL')
            else:
                columns_with_types.append(f'"{col}" TEXT')

        columns_with_types.append('"CustomerID" INTEGER')  # Add CustomerID as foreign key
        columns_with_types_str = ', '.join(columns_with_types)
        db.execute(f'CREATE TABLE "{table_name}" ({columns_with_types_str}, FOREIGN KEY ("CustomerID") REFERENCES "customerdetails"("CustomerID"))')

        # Insert data
        placeholders = ', '.join('?' for _ in columns)
        insert_sql = f'INSERT INTO "{table_name}" ({", ".join(columns)}) VALUES ({placeholders})'
        db.executemany(insert_sql, (tuple(int(row[col]) if col == 'CustomerID' and row[col].isdigit() else row[col] for col in columns) for row in reader))
    print(f"salesdetails table created with {len(columns)} columns.")

# Step 2: Data Transformation
def transform_data(db):
    
    """
    Transform data by calculating TotalAmount as Quantity * Price - Discount, but only for new records.
    
    """
    update_total_amount = '''
                            UPDATE salesdetails
                            SET TotalAmount = (Quantity * Price) - Discount
                            WHERE TotalAmount IS NULL OR TotalAmount = 0 OR TotalAmount = (Quantity * Price)
                            '''
    db.execute(update_total_amount)


# Step 3: Data Loading
def connect_to_database(db_name):
    return sqlite3.connect(db_name)

def query_database(query): 
    conn = connect_to_database('data/sales_transactions.db')
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# Step 3b: Combining the queries

def get_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('data/sales_transactions.db')
    sales_df = pd.read_sql_query("SELECT * FROM salesdetails", conn)
    customers_df = pd.read_sql_query("SELECT * FROM customerdetails", conn)
    conn.close()
    # Convert 'Date' column to datetime
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    return sales_df, customers_df

###############################################################################

#################### Update the database using the below f ####################

###############################################################################

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

###############################################################################

#################### Illustrate the required queries below ####################

###############################################################################


def extract_sales_last_quarter():
    start_of_last_quarter = '2023-10-01'
    end_of_last_quarter = '2023-12-31'
    query = f"""
    SELECT * FROM salesdetails
    WHERE Date >= '{start_of_last_quarter}' AND Date <= '{end_of_last_quarter}'
    """
    return query_database(query)



def calculate_total_sales_per_region():
    query = """
    SELECT Region, SUM(TotalAmount) as total_sales
    FROM salesdetails
    GROUP BY Region
    """
    return query_database(query)


# Join the sales data with a customer details table to find the total sales amount per customer
def total_sales_per_customer():
    query = """
    SELECT c.CustomerID, SUM(s.TotalAmount) as total_sales
    FROM salesdetails s
    JOIN customerdetails c ON s.CustomerID = c.CustomerID
    GROUP BY c.CustomerID
    """
    return query_database(query)


# Retrieve the top 10 products by sales amount in the last month (December 2023)
def top_10_products_last_month():
    start_of_last_month = '2023-12-01'
    end_of_last_month = '2023-12-31'
    query = f"""
    SELECT ProductID, SUM(TotalAmount) as total_sales
    FROM salesdetails
    WHERE Date >= '{start_of_last_month}' AND Date <= '{end_of_last_month}'
    GROUP BY ProductID
    ORDER BY total_sales DESC
    LIMIT 10
    """
    return query_database(query)


# Identify customers who have not made a purchase in the last six months (from 01/07/2023 to 31/12/2023)
def customers_no_purchase_last_six_months():
    six_months_ago = '2023-07-01'
    end_date = '2023-12-31'
    query = f"""
    SELECT * FROM customerdetails
    WHERE CustomerID NOT IN (
        SELECT DISTINCT CustomerID
        FROM salesdetails
        WHERE Date >= '{six_months_ago}' AND Date <= '{end_date}'
    )
    """
    return query_database(query)