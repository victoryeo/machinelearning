#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 09:50:55 2020

@author: vic
"""

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re
import requests

driver = webdriver.Chrome("/home/vic/workspace/chromedriver")

recipes={} # to store name of the recipe
prices={} # to store price of the recipe
driver.get("https://food.mthai.com/food-recipe")

content = driver.page_source
soup = BeautifulSoup(content)

sub = soup.findAll('article', {"id": re.compile("post")})
for index, thitem in enumerate(sub):
    httplink = thitem.find('a',{'href':re.compile('http')}).attrs['href']
    if ("recipe" in httplink):
        print(httplink)
        r = requests.get(httplink)
        content = r.content
        soup = BeautifulSoup(content)
        title = soup.find("h1", attrs={'class':'entry-title'}).text
        recipes[index] = {}
        recipes[index]['title'] = title
        #recipes[title] = {}
        for tditem in soup.find_all("p",text="ส่วนผสม"):
            ingredients = (tditem.find_next_sibling("ul"))
            #print(ingre)
            ingreditem = ingredients.find_all('li')
            for jndex, listitem in enumerate(ingreditem):
                print(listitem.text)
                recipes[index][jndex] = listitem.text

  
# write to csv file
user_ids = []
frames = []
for user_id, d in recipes.items():
    user_ids.append(user_id)
    frames.append(pd.DataFrame.from_dict(d, orient='index'))
    
pd.concat(frames, keys=user_ids).to_csv('/home/vic/workspace/recipes.csv', index=True, encoding='utf-8')
    
#df = pd.DataFrame({'Recipe Name':recipes,'Price':prices}) 
#df.to_csv('/home/vic/workspace/recipes.csv', index=False, encoding='utf-8')