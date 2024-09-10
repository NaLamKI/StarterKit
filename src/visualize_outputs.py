import json
import folium
from folium import IFrame
from http.server import SimpleHTTPRequestHandler
import os
import http.server
import socketserver
import threading
import webbrowser
import time


# Function to generate the map and save it as an HTML file
def generate_map(geojson, port):
    # init map in berlin
    m = folium.Map(location=[52.5162, 13.3777], zoom_start=8)

    # Loop through the GeoJSON features and add markers
    for feature in geojson['features']:
        # This script assumes one image, one value etc., per feature
        coordinates = feature['geometry']['coordinates']
        image_uri = feature['property']['datasets'][0]['items'][0]['images'][0]['uri']
        value_name = feature['property']['datasets'][0]['items'][0]['values'][0]['name']
        value = feature['property']['datasets'][0]['items'][0]['values'][0]['value']

        path = os.path.join('test/action/output', f"green_{image_uri}")
        image_url = f'http://localhost:{port}/{path}'

        # Create an iframe for the popup with the image
        html = f'<img src="{image_url}" style="width:448px;height:auto;"><br><p>{value_name}: {value:.2f}</p>'
        iframe = IFrame(html, width=500, height=400)
        popup = folium.Popup(iframe, max_width=448)

        icon = folium.CustomIcon(image_url, icon_size=(50, 50))
        folium.Marker(location=[coordinates['latitude'], coordinates['longitude']], icon=icon, popup=popup).add_to(m)

    # Save the map to an HTML file
    m.save('map.html')


# Function to start the server
def start_server(port):
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)

    # Open the HTML file in the web browser
    webbrowser.open(f'http://localhost:{port}/map.html')

    # Serve the directory in a new thread
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True  # Set as a daemon so it will be killed once the main thread is dead.
    thread.start()

    print(f"Serving on port {port}")
    return httpd, thread


# Function to stop the server
def stop_server(httpd, thread):
    httpd.shutdown()
    thread.join()
    print("Server stopped")


# Main execution
def main():
    port = 8000
    # Load the GeoJSON data
    with open('test/action/output/results.json') as f:
        geojson_data = json.load(f)

    generate_map(geojson_data, port)
    httpd, thread = start_server(port)

    # Wait for the browser to be closed
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        stop_server(httpd, thread)

        # Delete the generated file
        if os.path.exists('map.html'):
            os.remove('map.html')
            print("Map HTML file deleted")


if __name__ == "__main__":
    main()
