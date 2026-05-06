# WSAA-project
## Overview
This repository contains files relating to the final project for 8640 -- WEB SERVICES AND APPLICATIONS. This project is a web-based application that allows users to record and view trips they have taken to different countries. When a user adds a visit, the system automatically retrieves useful information about that country, such as its capital city and flag, using the [REST Countries API](https://restcountries.com/).

The application is built using:

- Flask to handle the web requests
- SQLite to store the data
- A dedicated data access layer to handle reading from and writing to the database
- REST Countries API to provide up-to-date country details

The project is hosted online using PythonAnywhere.

## Countries Data Sources
When a user creates a visit, they select a country using its 3-letter code (e.g. FRA for France) instead of the name. This code is sent to the backend and used to fetch full country details from the REST Countries API.

Using country codes allows direct lookup via the API’s alpha endpoint.

Example request:
```bash
https://restcountries.com/v3.1/alpha/FRA
```

## Hosting
This web-based application is hosted at the following base URL:
```bash
https://eChubb.pythonanywhere.com
```
## Project File Structure
```bash
WSAA-project/
│
├── server.py              # Flask API routes
├── visitDAO.py            # Database access layer (DAO)
├── createDB.py            # Creates SQLite tables
├── dbconfig.py            # Database configuration
├── travel.db              # SQLite database file
├── requirements.txt       # Dependencies
├── index.html             # frontend
├── style.css              # frontend
```
## Instruction for Local Setup
Should you wish to test or re-use the code, please take the following steps:

### 1. Clone repository
```bash
git clone https://github.com/EmmaChubbCode/WSAA-project.git
cd WSAA-project
```
### 2. Dependencies
```bash
pip install -r requirements.txt
```
### 3. Create database
```bash
python createDB.py
```
### 4. Run server
```bash
python server.py
```
Server runs at:
```bash
http://127.0.0.1:5000 
```
##  Database Design
The project uses an SQLite database (travel.db) with two tables:
```bash
CREATE TABLE countries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    capital TEXT,
    region TEXT,
    flag_url TEXT
);

CREATE TABLE visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_visited TEXT NOT NULL,
    notes TEXT,
    country_id INTEGER,
    FOREIGN KEY (country_id) REFERENCES countries(id)
);
```
### Notes:
- Each visit is linked to one country using country_id
- Data is retrieved using a SQL JOIN to combine visit and country information into a single API response.
- A country can appear in multiple visits
- This creates a one-to-many relationship

## API End Points

### Get all countries
```bash
GET /countries
```
For example:
```bash
curl https://eChubb.pythonanywhere.com/countries
```
### Get all visits
```bash
GET /visits
```
For example:
```bash
curl https://eChubb.pythonanywhere.com/visits
```
### Get visit by ID
```bash
GET /visits/<id>
```
For example:
```bash
curl https://eChubb.pythonanywhere.com/visits/1
```
### Create visit
```bash
POST /visits
```
For example:
```bash
curl -X POST https://eChubb.pythonanywhere.com/visits \
-H "Content-Type: application/json" \
-d '{
  "country": "FRA",
  "date_visited": "2024-03-12",
  "notes": "Great trip"
}'
```

### Update visit
```bash
PUT /visits/<id>
```
For example:
```bash
curl -X PUT https://eChubb.pythonanywhere.com/visits/1 \
-H "Content-Type: application/json" \
-d '{
  "date_visited": "2024-06-01",
  "notes": "Updated notes"
}'
```

### Delete visit
```bash
DELETE /visits/<id>
```
For example:
```bash
curl -X DELETE https://eChubb.pythonanywhere.com/visits/1
```

## Dependencies
This project uses the following libraries:

- Flask==3.0.0 – used to build the REST API and handle routing
- Werkzeug==3.0.1 – underlying WSGI utilities used by Flask
- Jinja2==3.1.2 – templating engine used by Flask
- click==8.1.7 – command-line utilities used by Flask
- itsdangerous==2.1.2 – used for secure data signing
- MarkupSafe==2.1.3 – safe string handling for templates
- requests==2.31.0 – used to fetch data from the REST Countries API
- flask-cors==5.0.1 – enables cross-origin requests between frontend and backend
- blinker==1.7.0 – signal support used internally by Flask
- importlib-metadata==6.8.0 – package metadata handling
- zipp==3.17.0 – zip file utilities used by dependencies
- colorama==0.4.6 – improves terminal output readability