#!/usr/bin/env python3.5

"""
See api_data/final_data/format.txt for details on how
output json files are formatted
"""

import json
import requests
import datetime
import time

####################
def formatSources():
   final_sources = [ ]
   
   with open('/var/www/html/cs373-idb/data/api_data/news_api_sources.json', 'r') as f:
      sources = json.load(f)['sources']
      
   with open('/var/www/html/cs373-idb/data/api_data/rest_countries_code_map.json', 'r') as f:
      country_code_map = json.load(f)
      
   with open('/var/www/html/cs373-idb/data/api_data/news_api_sources_language_map.json', 'r') as f:
      language_map = json.load(f)
      
   with open('/var/www/html/cs373-idb/data/api_data/newslookup_countries_region_map.json', 'r') as f:
      region_map = json.load(f)
      
   source_id = 1
   for source in sources:
      new_source = { }
      new_source['id_name'] = source['id']
      new_source['id_num'] = str(source_id)
      new_source['name'] = source['name']
      new_source['country'] = country_code_map[source['country'].upper()]
      new_source['language'] = language_map[source['language']]
      new_source['description'] = source['description']
      new_source['smallLogoURL'] = source['urlsToLogos']['small']
      new_source['mediumLogoURL'] = source['urlsToLogos']['medium']
      new_source['largeLogoURL'] = source['urlsToLogos']['large']
      new_source['category'] = source['category'].capitalize()
      new_source['external_link'] = source['url']
      new_source['region'] = region_map[source['country'].upper()]
      final_sources.append(dict(new_source))
      source_id += 1
      
   with open('/var/www/html/cs373-idb/data/api_data/final_data/final_sources.json', 'w') as f:
      json.dump(final_sources, f)

######################      
def formatLocations():
   final_locations = [ ]
   
   with open('/var/www/html/cs373-idb/data/api_data/rest_countries_all.json', 'r') as f:
      locations = json.load(f)
      
   with open('/var/www/html/cs373-idb/data/api_data/newslookup_countries_region_map.json', 'r') as f:
      region_map = json.load(f)
      
   with open('/var/www/html/cs373-idb/data/api_data/news_api_sources_language_map.json', 'r') as f:
      language_map = json.load(f)
      
   location_id = 1
   for location in locations:
      new_location = { }
      new_location['id_num'] = str(location_id)
      new_location['name'] = location['name']
      new_location['currencies'] = ", ".join(location['currencies'])
      new_location['region'] = region_map[location['alpha2Code']]
      
      if(len(location['latlng']) != 0):
         lat = location['latlng'][0]
         lng = location['latlng'][1]
         latlng = ["{0:.2f}".format(lat), "{0:.2f}".format(lng)]
         new_location['latlng'] = ", ".join(latlng)
      else:
         new_location['latlng'] = [ ]
      
      new_location['capital'] = location['capital']
      new_location['population'] = str(location['population'])
      new_location['topLevelDomain'] = ", ".join(location['topLevelDomain'])
      
      languages = location['languages']
      new_languages = [ ]
      for language in languages:
         new_languages.append(language_map[language])
      new_location['languages'] = ", ".join(new_languages)
      
      final_locations.append(dict(new_location))
      location_id += 1
   
   with open('/var/www/html/cs373-idb/data/api_data/final_data/final_locations.json', 'w') as f:
      json.dump(final_locations, f)
      
###################
def formatArticles():
   start = time.time()
   final_articles = [ ]
   
   newsAPI_articles, id_num = pull_newsAPI()
   numArticles1 = id_num-1
   newslookup_articles, numArticles2 = pull_newslookup(id_num)
   numArticles2 = numArticles2 - id_num
   
   final_articles += newsAPI_articles
   final_articles += newslookup_articles
   with open('/var/www/html/cs373-idb/data/api_data/final_data/final_articles.json', 'w') as f:
      json.dump(final_articles, f)
   end = time.time()
   elapsedTime = str(end - start)

   return numArticles1, numArticles2, elapsedTime

###################
def pull_newsAPI():
   with open('/var/www/html/cs373-idb/data/api_data/final_data/final_sources.json', 'r') as f:
      sources = json.load(f)
      
   apiKey = '836d24a3cd7c43bd9450a4496c2dbf41'
   url_part1 = 'https://newsapi.org/v1/articles?source='
   url_part2 = '&apiKey=' + apiKey

   newsAPI_articles = [ ]
   article_id = 1
   #print("Pulling from News API:")
   for source in sources:
      source_id_name = source['id_name']
      #print(source_id_name)
      response = requests.get(url_part1 + source_id_name + url_part2)
      response = response.json()
      if(response['status'] != "error"):
         articles = response['articles']
         for article in articles:
            new_article = { }
            new_article['id_num'] = str(article_id)
            new_article['title'] = article['title']
            new_article['description'] = article['description']
            new_article['source_name'] = source['name']
            new_article['category'] = source['category']
            if(article['publishedAt']):
               new_article['pubDate'] = article['publishedAt'].split('T')[0]
            else:
               new_article['pubDate'] = '0000-00-00'
            new_article['image_link'] = article['urlToImage']
            new_article['external_article_link'] = article['url']
            new_article['external_source_link'] = source['external_link']
            new_article['region'] = source['region']
            newsAPI_articles.append(dict(new_article))
            article_id += 1
         
   return newsAPI_articles, article_id

######################   
def pull_newslookup(article_id):
   with open('/var/www/html/cs373-idb/data/api_data/newslookup_regions_id_map.json', 'r') as f:
      region_map = json.load(f)
      
   with open('/var/www/html/cs373-idb/data/api_data/month_map.json', 'r') as f:
      month_map = json.load(f)

   client_id = '17122'
   secret = '32c77c1b83556dbf3c621247302af153'
   url_part1 = 'https://api.newslookup.com/feed/live?fmt=&region='
   url_part2 = '&output=json&client_id='
   url_part3 = '&secret='
   
   newslookup_articles = [ ]
   #print("Pulling from Newslookup:")
   for region in region_map.keys():
      #print(region_map[region])
      response = requests.get(url_part1 + region + url_part2 + client_id + url_part3 + secret)
      response = response.json()
      articles = response['items']
      for article in articles:
         new_article = { }
         new_article['id_num'] = str(article_id)
         new_article['title'] = article['title']
         
         if 'description' in article:
            new_article['description'] = article['description']
         else:
            new_article['description'] = 'No description available'
         
         new_article['source_name'] = article['source_title']
         
         if 'category' in article:
            new_article['category'] = article['category'].capitalize()
         else:
            new_article['category'] = 'General'
         
         pubDate = article['pubdate'].split()
         pubDate = datetime.date(int(pubDate[3]), month_map[pubDate[2]], int(pubDate[1]))
         new_article['pubDate'] = pubDate.isoformat()
         
         if 'image_link' in article:
            new_article['image_link'] = article['image_link']
         else:
            new_article['image_link'] = 'No image available'
         
         new_article['external_article_link'] = article['link']
         new_article['external_source_link'] = article['source_url']
         new_article['region'] = region_map[region]
         newslookup_articles.append(dict(new_article))
         article_id += 1
         
   return newslookup_articles, article_id

######################
def printEmailHeader():
   print('getData.py Summary')
   print('------------------------------')
   print(time.strftime('%m/%d/%Y %H:%M:%S'))

def printEmailSummary(numArticles1, numArticles2, elapsedTime):
   print('Runtime = ' + elapsedTime + ' sec')
   print(str(numArticles1) + ' articles pulled from News API')
   print(str(numArticles2) + ' articles pulled from Newslookup API')
   print(str(numArticles1 + numArticles2) + ' total articles pulled')
   print('getData Execution Success')

##########################
if __name__ == '__main__':
   #formatSources()
   #formatLocations()
   printEmailHeader()
   numArticles1, numArticles2, elapsedTime = formatArticles()
   printEmailSummary(numArticles1, numArticles2, elapsedTime)
