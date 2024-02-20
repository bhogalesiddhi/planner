from flask import Flask, render_template, request, jsonify
import requests
from utils import shortest_paths_recommandation


app = Flask(__name__)

# Function to fetch places based on coordinates
def fetch_places(lat_min, lat_max, lon_min, lon_max):
    url = f"https://api.opentripmap.com/0.1/en/places/bbox?lat_min={lat_min}&lat_max={lat_max}&lon_min={lon_min}&lon_max={lon_max}&apikey=5ae2e3f221c38a28845f05b6b4978fe8f6523357c1d4dd9e1b5e1363"
    response = requests.get(url)
    return response.json()

# Function to filter places based on user interests

    # Function to filter places based on user interests and sort them by rate
def filter_and_sort_places(places, interests):
    filtered_places = []
    for place in places['features']:
        for interest in interests:
            if interest in place['properties']['kinds']:
                filtered_places.append(place)
                break
    # Sort the filtered places based on rate
    filtered_places.sort(key=lambda x: x['properties']['rate'], reverse=True)
    return filtered_places


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/find_pois', methods=['GET'])
def find_pois():
    city = request.args.get('city')
    # Fetching city coordinates using the OpenTripMap API
    city_data = requests.get(f"https://api.opentripmap.com/0.1/en/places/geoname?name={city}&apikey=5ae2e3f221c38a28845f05b6b4978fe8f6523357c1d4dd9e1b5e1363").json()
    lat = city_data['lat']
    lon = city_data['lon']
    
    # Defining the bounding box coordinates for the city
    lat_min = lat - 0.1
    lat_max = lat + 0.1
    lon_min = lon - 0.1
    lon_max = lon + 0.1
    
    # Fetching places within the bounding box
    places = fetch_places(lat_min, lat_max, lon_min, lon_max)
    
    # Filtering places based on user interests
    interests = request.args.getlist('interests')
    filtered_and_sorted_places = filter_and_sort_places(places, interests)
    
    suggested_places = []
    detailed_info = []

    for place in filtered_and_sorted_places:
        if 'properties' in place and 'xid' in place['properties']:
            xid = place['properties']['xid']
            detailed_info_url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}?apikey=5ae2e3f221c38a28845f05b6b4978fe8f6523357c1d4dd9e1b5e1363"
            detailed_info_response = requests.get(detailed_info_url).json()
            detailed_info.append(detailed_info_response)
            suggested_places.append(place)

    
    spots = []
    for spot_info in detailed_info:
        spot = {
        'id': spot_info['xid'],
        'name': spot_info['name'],
        'location': (spot_info['point']['lat'], spot_info['point']['lon']),
        'type': spot_info['kinds'],
        'rating': spot_info['rate'],
        'url' : spot_info.get('url', '') , # Default value is an empty string if 'url' key is not present
        'preview_image': spot_info.get('preview', {}).get('source', ''), 
        # Add any other relevant details here
        }
        spots.append(spot)


       
    optimal_routes = shortest_paths_recommandation(spots, interests)
    print("Optimal Routes:", optimal_routes)
    # for i, route in enumerate(optimal_routes):
    #     print(f"Route {i + 1}:")
    #     for spot_id in route:
    #         print(f"- Spot ID: {spot_id}")
    #     print()

    
            
    return jsonify(detailed_info)





if __name__ == '__main__':
    app.run(debug=True)
