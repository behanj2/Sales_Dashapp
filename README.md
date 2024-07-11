project_root/
│
├── app.py: The main entry point for the Dash application.
├── server.py: Contains server configuration and settings for the Dash app.
├── HR_library.py: pySQL Lib, of all SQL functionality required for the project.
│
├── requirements.txt: Lists the Python dependencies required for the project.
├── README.md: Provides documentation and instructions for setting up and running the project.
│
├── sales_transactions.db: SQLite database containing sales transaction and customer data used by the Dash App. Updatable from csv files.
├── australia.geojson: GeoJSON file with geographical boundaries of Australian states.
├── customer_details.csv: CSV file containing customer details.
├── sales_transactions.csv: CSV file containing sales transaction data.
│
├── assets/
│   └── RT_Primary_Red_RGB.png: Rio Tinto logo image used in the application.
│
└── pages/
    ├── __init__.py: Initializes the pages module for the Dash app.
    ├── database.py: Contains the database creation, and database update functionality. The data refresh button is subprocessing this code.
    ├── overview.py: Contains the layout and logic for the overview page of the application. 
    ├── sales_by_region.py: Contains the layout and logic for the sales by region visualization.
    ├── top_customers.py: Contains the layout and logic for the top customers visualization.
    └── best_selling_products.py: Contains the layout and logic for the best-selling products visualization.

