from flask import Flask, request, jsonify, send_file
import requests
import zipfile
import os
from urllib.parse import urlparse
import shutil

#cel
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
 
@app.route('/zip', methods=['POST'])
def zip_files():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({'error': 'Request data must be in JSON format'}), 400
   
    # Extract file URLs from the JSON data
    json_data = request.json
    file_urls = json_data.get('files', [])
   
    # Create a temporary directory to store the downloaded files
    temp_dir = 'temp_zip'
    os.makedirs(temp_dir, exist_ok=True)
   
    # Download files from URLs and store them in the temporary directory
    downloaded_files = []
    for file_url in file_urls:
        file_path = download_file(file_url, temp_dir)
        if file_path:
            downloaded_files.append(file_path)
   
    # Create a zip file
    zip_file_name = 'zipped_files.zip'
    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        for file_path in downloaded_files:
            file_name = os.path.basename(file_path)
            zipf.write(file_path, file_name)
   
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
   
    # Return the relative path to the zip file
    return jsonify({'download_link': zip_file_name})
 
@app.route('/unzip', methods=['POST'])
def unzip_file():
    # Check if the request contains a list of file paths
    if 'files' not in request.json or not isinstance(request.json['files'], list):
        return jsonify({'error': 'No list of file paths found in the request or the list is empty'}), 400

    # Extract each zip file
    for file_path in request.json['files']:
        print(file_path)
        # Verify if the file exists
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found: {file_path}'}), 404
        
        # Extract the zip file
        zip_filename = os.path.basename(file_path)
        extract_path = os.path.join('folderhasilunzip', os.path.splitext(zip_filename)[0])
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

    return jsonify({'message': f'Zip files have been successfully extracted to "{file_path}"'})


@app.route('/download/<path:filename>', methods=['GET'])
def download_file2(filename):
    
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)