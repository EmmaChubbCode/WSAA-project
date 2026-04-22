# description: A simple Flask server to handle API requests for the frontend.
import requests
from flask import Flask, jsonify, request, abort
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

from visitDAO import visitDAO

app = Flask(__name__, static_url_path='', static_folder='.')

@app.route('/')
@cross_origin()
def index():
    return app.send_static_file('index.html')

# curl "http://127.0.0.1:5000/visits"
@app.route('/visits')
@cross_origin()
def getAll():
    results = visitDAO.getAllVisits()
    return jsonify(results)

# curl "http://127.0.0.1:5000/visits/2"
@app.route('/visits/<int:id>')
@cross_origin()
def findById(id):
    foundVisit = visitDAO.findVisitByID(id)
    if not foundVisit:
        abort(404)
    return jsonify(foundVisit)

# curl  -i -H "Content-Type:application/json" -X POST -d "{\"country\":\"ALB\",\"date_visited\":\"2024-03-12\",\"notes\":\"Loved it\"}" http://127.0.0.1:5000/visits
@app.route('/visits', methods=['POST'])
@cross_origin()
def createVisit():
    if not request.json:
        abort(400) # bad request, no json sent

    # get the country code sent from the dropdown e.g. "ALB" for Albania
    # the user sees the country name in the dropdown but the code is what gets submitted
    # we use the code instead of the name because /alpha/ is a direct lookup and more reliable than /name/
    countryCode = request.json.get('country')
    if not countryCode:
        abort(400)  # country code is required

    # call the REST Countries API using the 3 letter country code - https://restcountries.com/
    apiResponse = requests.get(f"https://restcountries.com/v3.1/alpha/{countryCode}")

    # the alpha endpoint can return a list or a single object depending on the country
    response = apiResponse.json()
    apiData = response[0] if isinstance(response, list) else response

    print("status code:", apiResponse.status_code)   # <-- add here
    print("response text:", apiResponse.text)
    # pull out the bits we want from the API response
    # you can see structure of the api response here: https://restcountries.com/v3.1/alpha/FRA
    countryData = {
        'name':     apiData['name']['common'],
        'capital':  apiData['capital'][0] if 'capital' in apiData else 'N/A',
        'region':   apiData['region'],
        'flag_url': apiData['flags']['png']
    }

    # save the country to our database if it isn't already there
    savedCountry = visitDAO.getOrCreateCountry(countryData)

    # build the visit using the country id we got back
    visit = {
        'date_visited': request.json.get('date_visited'),
        'notes':        request.json.get('notes', ''),
        'country_id':   savedCountry['id']
    }

    addedVisit = visitDAO.createVisit(visit)
    return jsonify(addedVisit), 201

# curl -i -H "Content-Type:application/json" -X PUT -d "{\"date_visited\":\"2024-06-01\",\"notes\":\"Updated notes\"}" http://127.0.0.1:5000/visits/1
@app.route('/visits/<int:id>', methods=['PUT'])
@cross_origin()
def updateVisit(id):
    foundVisit = visitDAO.findVisitByID(id)
    if not foundVisit:
        abort(404)

    if not request.json:
        abort(400)

    reqJson = request.json

    if 'date_visited' in reqJson:
        foundVisit['date_visited'] = reqJson['date_visited']
    if 'notes' in reqJson:
        foundVisit['notes'] = reqJson['notes']

    visitDAO.updateVisit(id, foundVisit)
    return jsonify(foundVisit)

# curl -i -X DELETE http://127.0.0.1:5000/visits/1
@app.route('/visits/<int:id>', methods=['DELETE'])
@cross_origin()
def deleteVisit(id):
    visitDAO.deleteVisit(id)
    return jsonify({"done": True})

# curl "http://127.0.0.1:5000/countries"
@app.route('/countries')
@cross_origin()
def getAllCountries():
    # returns all countries currently saved in our database
    results = visitDAO.getAllCountries()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)


