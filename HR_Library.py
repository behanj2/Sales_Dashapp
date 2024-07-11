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
    """Transform data by calculating TotalAmount as Quantity * Price - Discount, but only for new records."""
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
    conn = connect_to_database('sales_transactions.db')
    df = pd.read_sql(query, conn)
    conn.close()
    return df


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