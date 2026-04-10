# author: Emma Chubb
# Description: this script contains the data access object for the visits table
# mostly adapted from Andrew's code but updated to fit my two table design. 

import mysql.connector # library to connect to sql db.
import dbconfig as cfg # my config file wth my sql connection details.

class VisitDAO: # 
    connection = ""
    cursor = ""
    host =     ""
    user =     ""
    password = ""
    database = ""

    # pull connection details from dbconfig.py. see: https://docs.python.org/3/reference/datamodel.html#object.__init__
    def __init__(self):
        self.host =     cfg.mysql['host']
        self.user =     cfg.mysql['user']
        self.password = cfg.mysql['password']
        self.database = cfg.mysql['database']

    # create cursor that can run SQL commands. see: https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor.html 
    def getcursor(self):
        self.connection = mysql.connector.connect(
            host=     self.host,
            user=     self.user,
            password= self.password,
            database= self.database
        )
        self.cursor = self.connection.cursor()
        return self.cursor
    
    # close cursor and connection to free up resources. see: https://stackoverflow.com/questions/53230079/why-should-one-use-functions-cursor-and-connection-close-in-python-after-connect 
    def closeAll(self):
        self.connection.close()
        self.cursor.close()

    # First define the methods for working with the country table. 
    # we don't want to repeatedly add the same countries to this list if e.g. france is visited twice, so we need a method that checks if the country already exists before inserting.

    def getOrCreateCountry(self, countryData):
        # it first checks if the country is already in our database
        cursor = self.getcursor()
        sql = "SELECT * FROM countries WHERE name = %s"  # look for country by name, %s as placeholder. 
        cursor.execute(sql, (countryData['name'],))      # the comma makes it a tuple, required by mysql connector
        result = cursor.fetchone()                        # fetchone returns a single row or None if not found: https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-fetchone.html

        if result: # if the fetchone returns something.
            # country already exists in our db, no need to insert again
            self.closeAll()
            return self.convertToCountryDict(result)  # convert the row to a dictionary and return it

        # country not found so insert it into the countries table
        sql = "INSERT INTO countries (name, capital, region, flag_url) VALUES (%s, %s, %s, %s)"
        values = (countryData['name'], countryData['capital'], countryData['region'], countryData['flag_url'])
        cursor.execute(sql, values)
        self.connection.commit()       # commit makes the insert permanent in the database
        newid = cursor.lastrowid       # lastrowid give the auto generated id of the row we just inserted
        countryData['id'] = newid      # add the new id to the dictionary before returning it
        self.closeAll()
        return countryData

    def getAllCountries(self):
        # returns every row in the countries table as a list of dictionaries
        cursor = self.getcursor()
        cursor.execute("SELECT * FROM countries")
        results = cursor.fetchall()    # fetchall returns all rows as a list of tuples fetchall: https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-fetchall.html
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
            WHERE visits.id = %s
        """
        cursor.execute(sql, (id,))
        result = cursor.fetchone()   # only expecting one row back
        self.closeAll()
        return self.convertToVisitDict(result)

    def createVisit(self, visit):
        # inserts a new row into the visits table
        cursor = self.getcursor()
        sql = "INSERT INTO visits (date_visited, notes, country_id) VALUES (%s, %s, %s)"
        # .get('notes', '') means use the notes value if it exists, otherwise use empty string. see@ https://docs.python.org/3/library/stdtypes.html#dict.get
        values = (visit['date_visited'], visit.get('notes', ''), visit['country_id'])
        cursor.execute(sql, values)
        self.connection.commit()
        visit['id'] = cursor.lastrowid  # add the new id to the visit dictionary
        self.closeAll()
        return visit

    def updateVisit(self, id, visit):
        # updates an existing visit row - note we only allow changing date and notes because the country facts are fixed. 
        # country cannot be changed on a visit, you would delete and recreate instead
        cursor = self.getcursor()
        sql = "UPDATE visits SET date_visited = %s, notes = %s WHERE id = %s"
        values = (visit['date_visited'], visit.get('notes', ''), id)
        cursor.execute(sql, values)
        self.connection.commit()  # commit is required for any change that modifies data https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-commit.html 
        self.closeAll()

    def deleteVisit(self, id):
        # deletes a visit row by id
        cursor = self.getcursor()
        sql = "DELETE FROM visits WHERE id = %s"
        cursor.execute(sql, (id,))
        self.connection.commit()
        self.closeAll()

    def convertToCountryDict(self, row):
        # mysql returns rows as plain tuples e.g. (1, 'France', 'Paris', 'Europe', 'flag.png')
        # this converts that tuple into a dictionary so it can be returned as JSON
        keys = ['id', 'name', 'capital', 'region', 'flag_url']
        return {keys[i]: row[i] for i in range(len(keys))}

    def convertToVisitDict(self, row):
        # visits JOIN countries returns a flat tuple with columns from both tables
        # we manually map each position in the tuple to a named key (i.e. id, date_visited, notes, name, capital, region, flag_url)
        # the country details are nested inside their own dictionary within the visit
        return {
            'id':           row[0],
            'date_visited': str(row[1]),  # convert date object to string so it can be JSONified
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