import requests
from django.shortcuts import render

def say_hello(request):
    return render(request, 'hello.html', {"name": "rajja"})

def get_coordinates(location, api_key):
    url = f"https://geocode.maps.co/search?q={location}&api_key={api_key}"

    try:
        response = requests.get(url)
        
        # Log the raw response for debugging
        print(f"Geocoding API raw response for {location}: {response.text}")
        
        if response.status_code != 200:
            raise ValueError(f"Geocoding API returned status code {response.status_code} for {location}")
        
        data = response.json()

        if not data or len(data) == 0:
            raise ValueError(f"Geocoding API returned empty data for {location}")

        lat = data[0].get('lat')
        lon = data[0].get('lon')

        if not lat or not lon:
            raise ValueError(f"Failed to extract latitude and longitude for {location}")

        return lat, lon

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Request failed for {location}: {e}")
    except ValueError as ve:
        raise ValueError(ve)
    except Exception as e:
        raise ValueError(f"An unexpected error occurred while processing the Geocoding API response: {e}")
    


def get_destination_info(destination):
    # Replace with your own logic to get information about the destination
    # Example: Fetch from Wikipedia
    search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={destination}&limit=1&format=json"
    response = requests.get(search_url)

    if response.status_code == 200:
        data = response.json()
        if data[1]:  # Check if there are results
            description = data[2][0]  # First description
            link = data[3][0]  # Wikipedia link
            return description, link
    return "No description available.", "#"

# def get_images_from_unsplash(destination, access_key):
#     search_url = f"https://api.unsplash.com/search/photos?query={destination}&client_id={access_key}"
#     response = requests.get(search_url)

#     # Log the response for debugging
#     print(f"Unsplash API response for {destination}: {response.text}")

#     if response.status_code == 200:
#         data = response.json()
#         if data['results']:
#             images = [img['urls']['small'] for img in data['results']]
#             return images
#     return []


def calculate_distance(request):
    origin = request.GET.get('from')
    destination = request.GET.get('to')

    if not origin or not destination:
        return render(request, 'error.html', {"error": "Please provide both origin and destination."})

    try:
        geocode_api_key = "66ed2565f3694748353420thb8db5a7"
        origin_lat, origin_lon = get_coordinates(origin, geocode_api_key)
        destination_lat, destination_lon = get_coordinates(destination, geocode_api_key)

        distance_api_key = "U8XDkTT5HHg3cK7P3kaEnsAHtEYdoSd7PUbO8BAaXwMWQykreAboliu2AcyTyCR4"
        url = f"https://api.distancematrix.ai/maps/api/distancematrix/json?origins={origin_lat},{origin_lon}&destinations={destination_lat},{destination_lon}&key={distance_api_key}"

        response = requests.get(url)
        
        if response.status_code != 200:
            raise ValueError(f"Distance Matrix API returned status code {response.status_code}")

        data = response.json()

        if data.get('status') != 'OK':
            raise ValueError("Error with the Distance API request.")

        elements = data['rows'][0]['elements']
        if not elements or elements[0].get('status') == 'ZERO_RESULTS':
            raise ValueError("No results found for the provided locations.")

        distance_text = elements[0].get('distance', {}).get('text')
        duration_text = elements[0].get('duration', {}).get('text')
        distance_value = elements[0].get('distance', {}).get('value')  # Distance in meters

        cost_bike = (distance_value / 1000) * 10  # 10 PKR per km for bike
        cost_car = (distance_value / 1000) * 20   # 20 PKR per km for car

        destination_description, wikipedia_link = get_destination_info(destination)

        # Fetch real images from Unsplash
        unsplash_access_key = "66ed2565f3694748353420thb8db5a7"
        # image_gallery = get_images_from_unsplash(destination, unsplash_access_key)

        return render(request, 'result.html', {
            'distance': distance_text,
            'duration': duration_text,
            'origin': origin,
            'destination': destination,
            'origin_lat': origin_lat,
            'origin_lon': origin_lon,
            'destination_lat': destination_lat,
            'destination_lon': destination_lon,
            'cost_bike': cost_bike,
            'cost_car': cost_car,
            'destination_description': destination_description,
            'wikipedia_link': wikipedia_link,
            # 'image_gallery': image_gallery,
        })

    except (ValueError, KeyError, IndexError) as e:
        print(f"Error: {e}")
        return render(request, 'error.html', {"error": str(e)})
