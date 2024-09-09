import requests
import json
from collections import defaultdict
from datetime import datetime

import time
import subprocess
import os

# Define paths
file_path = 'output.html'
repo_dir = r'C:\Users\traum\Desktop\vs\discord\obi'

def git_command(command, cwd=repo_dir):
    """Run a git command in the given directory."""
    result = subprocess.run(command, cwd=cwd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error running command '{command}': {result.stderr}")
    return result

def check_file_update():
    """Check if the file has been updated."""
    return os.path.getmtime(file_path)

def commit_and_push():
    """Commit changes and push to GitHub."""
    git_command('git add output.html')
    git_command('git commit -m "Auto-commit updated file"')
    git_command('git push origin main')

def retrieve_messages(channel_id, token):
    print("Retrieving messages...")  # Debug print
    headers = {'Authorization': f'Bot {token}'}
    base_url = f'https://discord.com/api/v9/channels/{channel_id}/messages'
    
    messages = []
    params = {'limit': 50}  # Default limit for pagination
    while True:
        try:
            r = requests.get(base_url, headers=headers, params=params)
            r.raise_for_status()  # Raise an exception for HTTP errors

            batch = r.json()  # Parse the response as JSON
            if not batch:
                break  # No more messages to retrieve

            messages.extend(batch)  # Add the batch of messages to the list

            # Get the ID of the last message to use for pagination
            params['before'] = batch[-1]['id']

            # Introduce a short delay between requests to avoid hitting the rate limit
            time.sleep(1.5)  # 1.5 seconds delay to avoid rapid requests

        except requests.exceptions.HTTPError as e:
            if r.status_code == 429:  # Rate limited
                retry_after = r.json().get('retry_after', 1)  # Default to 1 second
                print(f"Rate limited. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)  # Wait before retrying
            else:
                print(f"Failed to retrieve messages: {e}")
                break
    
    print(f"Retrieved {len(messages)} messages")  # Debug printg
    print(json.dumps(messages[0], indent=4))  # Debug print one message structure

    return messages

def format_timestamp(timestamp):
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    return dt.strftime('%B %d, %Y %I:%M %p')  # Full month name, 12-hour clock, AM/PM f

def extract_unique_embed_info(messages): #this handles the counts for each url, unique
    url_data = {} #this is the array that holds each field from extraction
    url_counts = defaultdict(int) #this initializes each value to the key of zero

    for message in messages: # this goes thru each message
        for embed in message.get('embeds', []): #for each message, it looks for the key embed, and gets the array[]
            url = embed.get('url') #this sets the variable url, which we are basing our count on to the array of embed, then the key or url, and getting its value
            if url: #if there is a value
                url_counts[url] += 1 #we put that in our array and initialize it with one
                if url not in url_data: #if the value is not in the array already..(so if example is already there its not going to add it again, the count is already being taken above, and will be paired with this unique output)
                    data = {} #it makes a new array for the unique value with the key of data, data will have its own values(url, description, image url, timestamp, original price)
                    data['url'] = url #this sets the key url, in the data array of this message, to the url extracted
                    data['description'] = embed.get('description')
                    image = embed.get('image', {}) #for this we get image keys and values and make image an array with its keys and values, so image may have, keys like author, size, url, and others attached to it
                    data['image_url'] = image.get('url') #now we set the image url key for this data set to the image(object array) and extract the key value of url(get gets the value of the key)

                    # Extract and format timestamp
                    timestamp = embed.get('timestamp')#set the timestamp variable to in embeds, there is a direct key called timestamp, so its value using its parent(embed) is stored in the timestamp variable
                    if timestamp:#if this is true
                        data['timestamp'] = format_timestamp(timestamp)#we set the key of timestamp in the dataset to the formatted version of the variable timestamp by calling our previous function we made (format_timestamp)

                    fields = embed.get('fields', [])#since fields is another main child of messages, so far..embeds, fields we have to populate that object using get, and setting that key to an array
                    for field in fields:#now we go thru each of the fields as field in fields and get the value of the field 'name', for each
                        if field.get('name') == 'Original Price':#so now we take our object(field) and get the value of the name field, which is one of the two keys in the field array, if the value of the name key is original price we proceed
                            data['original_price'] = field.get('value')#if the name's value(as in key value) is equal to 'original price', we get the value from the key value, so field has two keys, name and value.
                            break#so it keeps searching for the value of original price in the name field once it stores this it breaks
                    
                    url_data[url] = data #remember since we are only doing unique entries, we base this whole thing on if url is not in url, so we can add to our array, and the key will be the url, its value will be all the key values in the data array
                                         #we can now parse each unique url from the url_data array each key will be a url, that's value will be contained in our data array built above

    # Add count field to each unique entry
    for url, data in url_data.items():#when url is the key, in the data array, that's in the url_data array it adds data count to those items like data[description] 
        data['count'] = url_counts[url]#it uses the url we are on and adds the key count with the value extracted from the array url_counts using the url as a key
    
    return list(url_data.values())#this takes the url_data array and gets the values which are the final value of the last key the key is the url, each url has a data dictionary that has key values these are the values we get, and turn to a list
                                  #so what it does is take the url_data object that has keys or url for each url key the value is a data dictionary we turned down to the key we want its value, so this just gets all the values
                                  #related to that url

def generate_html(extracted_info):
    # Define a basic HTML template with Bootstrap
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Extracted Data</title>
        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f8f9fa;
            }
            .card {
                border: 1px solid #ddd;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .card-title a {
                color: #007bff;
                text-decoration: none;
            }
            .card-title a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row">
                {% for item in extracted_info %}
                <div class="col-md-4 mb-4">
                    <div class="card">
                        <img class="card-img-top" src="{{ item.image_url }}" alt="Image">
                        <div class="card-body">
                            <h5 class="card-title"><a href="{{ item.url }}" target="_blank">{{ item.description }}</a></h5>
                            <p class="card-text">Original Price: {{ item.original_price }}</p>
                            <p class="card-text">Timestamp: {{ item.timestamp }}</p>
                            <p class="card-text">Quantity: {{ item.count }}</p>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"></script>
    </body>
    </html>
    """

    # Create a Jinja2 Template instance
    template = Template(html_template)
    
    # Render the template with the extracted_info data
    html_output = template.render(extracted_info=extracted_info)

    return html_output

def main():
    print("Starting script...")  # Debug print
    channel_id = '1273656579862040587'  # Your channel ID
    
    messages = retrieve_messages(channel_id, token)
    extracted_info = extract_unique_embed_info(messages)
    html_content = generate_html(extracted_info)
    
    previous_mtime = check_file_update()  # Get the initial modification time
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

    # Monitor for file updates
    while True:
        time.sleep(10)  # Check every 10 seconds
        current_mtime = check_file_update()
        if current_mtime != previous_mtime:
            print("File updated. Committing and pushing changes...")
            commit_and_push()
            previous_mtime = current_mtime

if __name__ == "__main__":
    main()

