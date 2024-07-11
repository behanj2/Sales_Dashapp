# Project Structure

project_root/ <br />
│<br />
├── app.py: The main entry point for the Dash application.<br />
├── server.py: Contains server configuration and settings for the Dash app.<br />
├── HR_library.py: pySQL Lib, of all SQL functionality required for the project.<br />
│<br />
├── requirements.txt: Lists the Python dependencies required for the project.<br />
├── README.md: Provides documentation and instructions for setting up and running the project.<br />
│<br />
├── sales_transactions.db: SQLite database containing sales transaction and customer data used by the Dash App. Updatable from csv files.<br />
├── australia.geojson: GeoJSON file with geographical boundaries of Australian states.<br />
├── customer_details.csv: CSV file containing customer details.<br />
├── sales_transactions.csv: CSV file containing sales transaction data.<br />
│<br />
├── assets/<br />
│   └── RT_Primary_Red_RGB.png: Rio Tinto logo image used in the application.<br />
│<br />
└── pages/<br />
    ├── __init__.py: Initializes the pages module for the Dash app.<br />
    ├── database.py: Contains the database creation, and database update functionality. The data refresh button is subprocessing this code.<br />
    ├── overview.py: Contains the layout and logic for the overview page of the application. <br />
    ├── sales_by_region.py: Contains the layout and logic for the sales by region visualization.<br />
    ├── top_customers.py: Contains the layout and logic for the top customers visualization.<br />
    └── best_selling_products.py: Contains the layout and logic for the best-selling products visualization.<br />

