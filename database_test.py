# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 14:34:20 2024

@author: Joseph.Behan


"""

#1 now we have set the csv into a databse


import csv
import sqlite3
import pandas as pd

def create_customerdetails_table(filename, db):
    """Create the customerdetails table in the database from a CSV file."""
    print(f"Creating customerdetails table from {filename}...")
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        table_name = 'customerdetails'
        
        # Drop table if it exists
        db.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        
        # Create table
        db.execute(f'CREATE TABLE "{table_name}" ("CustomerID" INTEGER PRIMARY KEY)')
        
        # Insert data
        customers = {row['CustomerID'] for row in reader}  # Use a set to ensure uniqueness
        insert_sql = f'INSERT INTO "{table_name}" ("CustomerID") VALUES (?)'
        db.executemany(insert_sql, [(customer,) for customer in customers])
    print(f"customerdetails table created with {len(customers)} unique CustomerID(s).")

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
        insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'
        db.executemany(insert_sql, (tuple(row[col] for col in columns) for row in reader))
    print(f"salesdetails table created with {len(columns)} columns.")

# Connect to the SQLite database and create tables
db_name = 'sales_transactions.db'
conn = sqlite3.connect(db_name)
create_customerdetails_table('C:/Users/joseph.behan/Local Projects - Temp/HR_DATA/sales_transactions.csv', conn)  # Update 'path_to_sales_transactions_csv' to the actual path
create_salesdetails_table('C:/Users/joseph.behan/Local Projects - Temp/HR_DATA/sales_transactions.csv', conn)  # Update 'path_to_sales_transactions_csv' to the actual path
conn.commit()
conn.close()



