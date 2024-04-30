from flask import Flask, request, jsonify, send_file
import requests
import os
from urllib.parse import urlparse
import shutil
from urllib.parse import unquote
from datetime import datetime as dt
 
app = Flask(__name__)
 
def download_file(url, dest_folder):
    # Parse the URL to get the filename
    parsed_url = urlparse(url)
    file_name = os.path.basename(parsed_url.path)
   
    # Download the file
    response = requests.get(url)
    if response.status_code == 200:
        # Save the file to the destination folder
        file_path = os.path.join(dest_folder, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path
    else:
        return None
 
def clear_userzip_folder():
    userzip_folder = 'userzip'
    if os.path.exists(userzip_folder):
        shutil.rmtree(userzip_folder)
    os.makedirs(userzip_folder, exist_ok=True)
   
@app.route('/zip', methods=['POST'])
def zip_files():
    clear_userzip_folder()
   
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({'error': 'Request data must be in JSON format'}), 400
   
    # Extract file URLs from the JSON data
    json_data = request.json
    file_urls = json_data.get('files', [])
   
    # Generate download link
    download_link = request.url_root + 'download?urls=' + '&urls='.join(file_urls)
   
    # Return the download link
    return jsonify({'download_link': download_link})
 
 
@app.route('/download', methods=['GET'])
def download_files():
    clear_userzip_folder()
    urls = request.args.getlist('urls')
    if not urls:
        return "Please provide 'urls' parameter in the query string", 400
   
    # Initialize a list to store file names
    file_names = []
   
    try:
        # Download each file from the provided URLs
        for url in urls:
            # Unquote the URL to handle special characters
            url = unquote(url)
           
            # Send a GET request to the provided URL
            response = requests.get(url)
            if response.status_code != 200:
                return f"Failed to download file from {url}. Status code: {response.status_code}", 500
           
            # Extract file name from URL
            file_name = url.split('/')[-1].split('?')[0]
           
            # Save the file temporarily
            with open(file_name, 'wb') as f:
                f.write(response.content)
           
            # Add file name to the list
            file_names.append(file_name)
       
        # Zip files into a single archive
        c = dt.now()
        zip_file_name = rf'userzip\downloaded_files_{c.strftime("%H_%M_%S")}.zip'
        import zipfile
        with zipfile.ZipFile(zip_file_name, 'w') as zipf:
            for file in file_names:
                zipf.write(file)
 
        # Remove temporary files
        for file in file_names:
            os.remove(file)
 
        # Send the zip file as a response
        return send_file(zip_file_name, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500
 
if __name__ == '__main__':
    app.run(debug=True)
 