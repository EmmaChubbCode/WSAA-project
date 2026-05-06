# author: Emma Chubb
# description: This file defines the database configuration for the application.
# It sets the correct file path for the SQLite database so it works both locally
# and when deployed on PythonAnywhere, regardless of the current working directoryy.

import os
# Get the absolute path of the current directory (project folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build full path to the SQLite database file to ensure it is always correctly located
database = os.path.join(BASE_DIR, "travel.db")