import requests

def get_location_coordinates(location):
    """
    Get the latitude and longitude coordinates for a given location using the OpenCage Geocoding API.

    Args:
        location (str): The location for which you want coordinates.

    Returns:
        dict: A dictionary containing 'latitude' and 'longitude' if successful, None otherwise.
    """
    # Replace with your valid OpenCage API key
    api_key = "b763ce4384594b87b725aa8f18cf46f8"
    base_url = "https://api.opencagedata.com/geocode/v1/json"
    
    params = {
        'key': api_key,
        'q': location,
        'limit': 1,  # Retrieve only the top result
        'pretty': 1  # Optional: makes the JSON response more readable
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)  # Set timeout to avoid hanging
        response.raise_for_status()  # Raise HTTPError for bad HTTP responses

        data = response.json()

        # Check if the response contains results
        if response.status_code == 200 and data.get('results'):
            lat = data['results'][0]['geometry']['lat']
            lon = data['results'][0]['geometry']['lng']
            return {'latitude': lat, 'longitude': lon}
        else:
            # Handle specific error messages from OpenCage API
            error_message = data.get('status', {}).get('message', 'Unknown error occurred')
            print(f"Error: {error_message}")
            return None

    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        print(f"Network error: {e}")
        return None
    except KeyError as e:
        # Handle missing keys in the JSON response
        print(f"Unexpected response format: {e}")
        return None
