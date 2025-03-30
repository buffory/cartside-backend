from bs4 import BeautifulSoup
import json

# Read the HTML file
with open('scrape.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find the script tag with id "__NEXT_DATA__"
next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})

if next_data_script:
    # Extract the JSON content
    json_data = json.loads(next_data_script.string)
    
    # Save to a file
    with open('next_data.json', 'w', encoding='utf-8') as outfile:
        json.dump(json_data, outfile, indent=2)
    
    print("JSON data successfully extracted and saved to next_data.json")
else:
    print("Script tag with id '__NEXT_DATA__' not found")

