# author: emma chubb
# description: This script sets up the country and visits tables. 
# they start off empty but as the user adds to visits, bth tables will be populated over time.


# mysql connector allows python to access mysql databases. https://pypi.org/project/mysql-connector-python/ 

# Step 1 Create database. use Andrew's code.

import mysql.connector

db = mysql.connector.connect(
  host="localhost",
  user="root",
  password=""
)

cursor = db.cursor()

cursor.execute("create DATABASE wsaa")

db.close()
cursor.close()

# Step 2 create tables. Modify Andrew's code. 

# connect to db again but this time specify the database we just created.
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="wsaa"
)
# create a cursor object to execute SQL commands.
cursor = db.cursor()

# use SQL to create countries. this is master list of countries and their details. 
cursor.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        id       INT AUTO_INCREMENT PRIMARY KEY,
        name     VARCHAR(100) NOT NULL,
        capital  VARCHAR(100),
        region   VARCHAR(100),
        flag_url VARCHAR(255)
    )
""")

# use sql to create visits. this will be populated by the user. it has foreign key to countries so we can link visits to specific countries.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS visits (
        id           INT AUTO_INCREMENT PRIMARY KEY,
        date_visited DATE NOT NULL,
        notes        VARCHAR(500),
        country_id   INT,
        FOREIGN KEY (country_id) REFERENCES countries(id)
    )
""")

print("Database and tables created successfully")

db.close()
cursor.close()