# author: emma chubb
# description: This script sets up the country and visits tables. 
# they start off empty but as the user adds to visits, bth tables will be populated over time.


# mysql connector allows python to access mysql databases. https://pypi.org/project/mysql-connector-python/ 

# Step 1 Create database. use Andrew's code.

import sqlite3
import dbconfig as cfg
database = cfg.database

con = sqlite3.connect(database)
cur = con.cursor()

# use sql to create countries. this is a master list of countries and their details.
cur.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT NOT NULL,
        capital  TEXT,
        region   TEXT,
        flag_url TEXT
    )
""")

# use sql to create visits. this will be populated by the user. it has a foreign key to countries so we can link visits to specific countries.
cur.execute("""
    CREATE TABLE IF NOT EXISTS visits (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        date_visited TEXT NOT NULL,
        notes        TEXT,
        country_id   INTEGER,
        FOREIGN KEY (country_id) REFERENCES countries(id)
    )
""")

con.commit()
print("Database and tables created successfully")

con.close()