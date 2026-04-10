# description: A simple Flask server to handle API requests for the frontend.
import requests
from flask import Flask, jsonify, request, abort
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

from visitDAO import visitDAO

app = Flask(__name__, static_url_path='', static_folder='.')

#app = Flask(__name__)

@app.route('/')
@cross_origin()
def index():
    return "Hello, World!"

# curl "http://127.0.0.1:5000/visits"
@app.route('/visits')
@cross_origin()
def getAll():
    #print("in getall")
    results = visitDAO.getAll()
    return jsonify(results)


#curl "http://127.0.0.1:5000/visits/2"
@app.route('/visits/<int:id>')
@cross_origin()
def findById(id):
    foundVisit = visitDAO.findByID(id)
    if not foundVisit:
        abort(404)
    return jsonify(foundVisit)

#curl  -i -H "Content-Type:application/json" -X POST -d "{\"title\":\"hello\",\"author\":\"someone\",\"price\":123}" http://127.0.0.1:5000/visits
@app.route('/visits', methods=['POST'])
@cross_origin()
def createVisit():
    
    if not request.json:
        abort(400) # bad request, no json  sent
      
      # get the country name the user typed in
    countryName = request.json.get('country')
    if not countryName:
        abort(400)  # country name is required

  # call the REST Countries API to get country details https://restcountries.com/
    apiResponse = requests.get(f"https://restcountries.com/v3.1/name/{countryName}") #copied from api docs.
    
    # take first result returned by api (might change later)
    apiData = apiResponse.json()[0]
   # pull out the bits we want from the API response.
   # you can see structure of thr api response here: https://restcountries.com/v3.1/name/France 
    countryData = {
        'name':     apiData['name']['common'],
        'capital':  apiData['capital'][0] if 'capital' in apiData else 'N/A',
        'region':   apiData['region'],
        'flag_url': apiData['flags']['png']
    }

    # save the country to our database if it isn't already there
    savedCountry = visitDAO.getOrCreateCountry(countryData)

    # build the visit using the country id we got back. Havent built frontend yet so double check these after.
    visit = {
        'date_visited': request.json.get('date_visited'),
        'notes':        request.json.get('notes', ''),
        'country_id':   savedCountry['id']
    }

    addedVisit = visitDAO.createVisit(visit)
    return jsonify(addedVisit), 201