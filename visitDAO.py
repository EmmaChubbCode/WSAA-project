# author: Emma Chubb
# Description: this script contains the data access object for the visits table
# adapted from Andrew's code but updated to fit my two table design.
# switched from mysql to sqlite3 for pythonanywhere free tier compatibility.
# docs: https://docs.python.org/3/library/sqlite3.html

import sqlite3
import dbconfig as cfg

class VisitDAO:
    connection = ""
    cursor = ""
    database = ""

    # pull database path from dbconfig.py. see: https://docs.python.org/3/reference/datamodel.html#object.__init__
    def __init__(self):
        self.database = cfg.database

    # create cursor that can run SQL commands.
    # check_same_thread=False is needed for Flask which can use multiple threads.
    # see: https://docs.python.org/3/library/sqlite3.html#sqlite3.connect
    def getcursor(self):
        self.connection = sqlite3.connect(self.database, check_same_thread=False)
        self.cursor = self.connection.cursor()
        return self.cursor

    # close cursor and connection to free up resources.
    # see: https://stackoverflow.com/questions/53230079/why-should-one-use-functions-cursor-and-connection-close-in-python-after-connect
    def closeAll(self):
        self.cursor.close()
        self.connection.close()

    # First define the methods for working with the country table.
    # we don't want to repeatedly add the same countries to this list if e.g. france is visited twice,
    # so we need a method that checks if the country already exists before inserting.

    def getOrCreateCountry(self, countryData):
        # it first checks if the country is already in our database
        cursor = self.getcursor()
        # sqlite3 uses ? as placeholder instead of %s in mysql
        sql = "SELECT * FROM countries WHERE name = ?"
        cursor.execute(sql, (countryData['name'],))      # the comma makes it a tuple, required by sqlite3
        result = cursor.fetchone()                        # fetchone returns a single row or None if not found: https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.fetchone

        if result: # if fetchone returns something, country already exists
            self.closeAll()
            return self.convertToCountryDict(result)  # convert the row to a dictionary and return it

        # country not found so insert it into the countries table
        sql = "INSERT INTO countries (name, capital, region, flag_url) VALUES (?, ?, ?, ?)"
        values = (countryData['name'], countryData['capital'], countryData['region'], countryData['flag_url'])
        cursor.execute(sql, values)
        self.connection.commit()       # commit makes the insert permanent in the database
        newid = cursor.lastrowid       # lastrowid gives the auto generated id of the row we just inserted
        countryData['id'] = newid      # add the new id to the dictionary before returning it
        self.closeAll()
        return countryData

    def getAllCountries(self):
        # returns every row in the countries table as a list of dictionaries
        cursor = self.getcursor()
        cursor.execute("SELECT * FROM countries")
        results = cursor.fetchall()    # fetchall returns all rows as a list of tuples: https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.fetchall
        returnArray = []
        for result in results:
            returnArray.append(self.convertToCountryDict(result))  # convert each row to a dictionary
        self.closeAll()
        return returnArray

    # ok now the visit methods

    def getAllVisits(self):
        cursor = self.getcursor()
        # join so we can get info from both tables.
        # see: https://www.w3schools.com/sql/sql_join.asp
        sql = """
            SELECT visits.id, visits.date_visited, visits.notes,
                   countries.name, countries.capital, countries.region, countries.flag_url
            FROM visits
            JOIN countries ON visits.country_id = countries.id
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        returnArray = []
        for result in results:
            returnArray.append(self.convertToVisitDict(result))  # convert each row to a nested dictionary
        self.closeAll()
        return returnArray

    def findVisitByID(self, id):
        # same JOIN query as above but filtered to one specific visit by id
        cursor = self.getcursor()
        sql = """
            SELECT visits.id, visits.date_visited, visits.notes,
                   countries.name, countries.capital, countries.region, countries.flag_url
            FROM visits
            JOIN countries ON visits.country_id = countries.id
            WHERE visits.id = ?
        """
        cursor.execute(sql, (id,))
        result = cursor.fetchone()   # only expecting one row back
        self.closeAll()
        return self.convertToVisitDict(result)

    def createVisit(self, visit):
        # inserts a new row into the visits table
        cursor = self.getcursor()
        sql = "INSERT INTO visits (date_visited, notes, country_id) VALUES (?, ?, ?)"
        # .get('notes', '') means use the notes value if it exists, otherwise use empty string. see: https://docs.python.org/3/library/stdtypes.html#dict.get
        values = (visit['date_visited'], visit.get('notes', ''), visit['country_id'])
        cursor.execute(sql, values)
        self.connection.commit()
        visit['id'] = cursor.lastrowid  # add the new id to the visit dictionary
        self.closeAll()
        return visit

    def updateVisit(self, id, visit):
        """
        Updates an existing visit record in the visits table.
        Only date_visited and notes can be changed because the country facts are fixed.
        Country cannot be changed on a visit, you would delete and recreate instead.
        Parameters:
            id (int): the id of the visit row to update
            visit (dict): dictionary containing 'date_visited' and 'notes'
        Docs:
            SQL UPDATE: https://www.w3schools.com/sql/sql_update.asp
            dict.get(): https://docs.python.org/3/library/stdtypes.html#dict.get
        """
        cursor = self.getcursor()
        sql = "UPDATE visits SET date_visited = ?, notes = ? WHERE id = ?"
        values = (visit['date_visited'], visit.get('notes', ''), id)
        cursor.execute(sql, values)
        self.connection.commit()  # commit is required for any change that modifies data: https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.commit
        self.closeAll()

    def deleteVisit(self, id):
        # deletes a visit row by id
        cursor = self.getcursor()
        sql = "DELETE FROM visits WHERE id = ?"
        cursor.execute(sql, (id,))
        self.connection.commit()
        self.closeAll()

    def convertToCountryDict(self, row):
        # sqlite3 returns rows as plain tuples e.g. (1, 'France', 'Paris', 'Europe', 'flag.png')
        # this converts that tuple into a dictionary so it can be returned as JSON
        keys = ['id', 'name', 'capital', 'region', 'flag_url']
        return {keys[i]: row[i] for i in range(len(keys))}

    def convertToVisitDict(self, row):
        # visits JOIN countries returns a flat tuple with columns from both tables
        # we manually map each position in the tuple to a named key (i.e. id, date_visited, notes, name, capital, region, flag_url)
        # the country details are nested inside their own dictionary within the visit
        return {
            'id':           row[0],
            'date_visited': str(row[1]),  # convert to string so it can be JSONified
            'notes':        row[2],
            'country': {                  # nested dictionary for country details
                'name':     row[3],
                'capital':  row[4],
                'region':   row[5],
                'flag_url': row[6]
            }
        }

# creates a single instance of the DAO that server.py will import and use
# this means there is only ever one DAO object shared across the whole app
visitDAO = VisitDAO()