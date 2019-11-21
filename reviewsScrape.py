from bs4 import BeautifulSoup
import json
import requests
import pandas as pd



def parse_review(review): 
    name = review['author']['name']
    date = review['datePublished']
    headline = review['headline']
    review_body = review['reviewBody']
    review_rating = int(review['reviewRating']['ratingValue'])
    language = review['inLanguage']
    return {'author': name, 'date':date, 'headline':headline, 
    'review_body':review_body, 'review_rating':review_rating, 'language':language}

def extract_reviews(bs):
    obj = bs.find('script', {'type':'application/ld+json'}).getText().replace(';','')
    review_data = json.loads(obj)
    reviews_raw = [item for item in review_data[0]['review']]
    reviews = [parse_review(item) for item in reviews_raw]
    return reviews
    

def is_last_page(bs):
    next_page = bs.find('link', attrs = {'rel':'next'})
    if next_page is None:
        return True
    else:
        return False

def scrape(url, company, target_path = './'):
    
    check_url = "http://"+url
    if requests.get(check_url).status_code != 200:
        print("Could not connect to " + url )
        print("Response : " + str(requests.get(check_url).status_code))
        return
    
    i = 1
    query = check_url + '?page='+ str(i)
    bs = BeautifulSoup(requests.get(query).text, 'html.parser')
    
    all_reviews = []
    
    while not is_last_page(bs):
        # Extract Reviews
        all_reviews = all_reviews + extract_reviews(bs)
        
        # Load the next page
        i += 1
        query = 'http://' + url + '?page='+ str(i)
        bs = BeautifulSoup(requests.get(query).text, 'html.parser')
    else:
        all_reviews = all_reviews + extract_reviews(bs)
        
    all_reviews = pd.DataFrame.from_dict(all_reviews)
    all_reviews['itemName'] = company
    
    all_reviews.to_json(target_path + company + '.json', orient="table")
    filename = name + ".json"
    with open(filename,'r') as jsonfile:
        parsed = json.load(jsonfile)
        parsed["name"] = company
        parsed["averageRating"] = round(float(all_reviews["review_rating"].mean()),1)
        del parsed['schema']
        parsed["reviews"] = parsed.pop("data")
        parsed["ratingSystem"] = "star"
        parsed["bestRating"] = int(all_reviews["review_rating"].max())
        parsed["lowestRating"] = int(all_reviews["review_rating"].min())
        parsed["numberReviews"] = len(all_reviews.index)
    with open('result.json', 'w') as f:
        obj = json.dumps(parsed, indent = 4, sort_keys = True)
        f.write(obj)

name = "wallgreens"

refined_name = name.lower()
refined_name = refined_name.strip()

url = "www.trustpilot.com/review/www."+name+".com"
scrape(url, name ,"./")




