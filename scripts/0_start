import sqlite3
import os
from _constants import db_path

paths = ["data/monthly_reports", "data/yearly_reports", "data/results"] #define nome das pastas a serem criadas

# if database does not exist, create it
if not os.path.exists(db_path):
    # create database connection
    conn = sqlite3.connect(db_path)
    # close connection
    conn.close()
    print("Database created successfully.")
else:
    print("Database already exists.")

# if paths dont exist, create them
for pasta in paths:
    if not os.path.exists(pasta):
        os.makedirs(pasta)

print("Paths created successfully.")
print("Add your xlsx files to the monthly_reports and yearly_reports folders and run the scripts.")