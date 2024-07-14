# Library Initialization.
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests                                            
from pymongo import MongoClient
import time
import datetime as dt
from mongoclienturl import mongo_client_url

# Flask Initialization.
app = Flask(__name__, static_folder='static')

# (MongoDB) configuration.
mongo_client = MongoClient(mongo_client_url)
db = mongo_client['<your database>']
collection = db['<your collection>']

# (MongoDB) Function to save document to the collection of links fetch from the crawler.
def save_to_mongodb(url, status):
    timestamp = time.time()
    real_time = dt.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    data_to_insert = {
        'url': url,
        'status': status,
        'timestamp': timestamp,
        'real_time': real_time
    }
    collection.insert_one(data_to_insert)
    return data_to_insert

# Function to get all links from <a> tag and separates faulty links.
@app.route('/crawl', methods=['POST'])
def crawl():
    url = request.form.get('url')
    if not url:
        return render_template('results.html', error_links=[])  
    
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        
        error_status_codes = {4, 5}  
        
        error_links = set()
        for link in links:
            href = link.get('href')
            if href.startswith('http') or href.startswith('https'):
                try:
                    link_response = requests.head(href, allow_redirects=True)
                    status_code = link_response.status_code
                    if status_code // 100 in error_status_codes:  
                        error_links.add(f"{href} - {status_code}")
                    save_to_mongodb(href,status_code)
                except requests.exceptions.RequestException:
                    error_links.add(f"{href} - Connection error")
                except Exception:
                    error_links.add(f"{href} - Unknown error")
        return render_template('results.html', error_links=error_links)
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
# Flask (landing page)
@app.route('/test')
def home():
    link = "http://127.0.0.1:5500/templates/test.html"
    return render_template('landing.html', link=link)

# Flask (Features page)
@app.route('/features')
def features():

    link = "http://127.0.0.1:5500/templates/features.html"
    return render_template('features.html', link=link)

# Flask (Why do we use it page)
@app.route('/hiw')
def hiw():
    link = "http://127.0.0.1:5500/templates/hiw.html"
    return render_template('hiw.html', link=link)

# Flask (Contact us page)
@app.route('/contactus')
def contactus():
    link = "http://127.0.0.1:5500/templates/contactus.html"
    return render_template('contactus.html', link=link)


if __name__ == '__main__':
    app.run(debug=True)