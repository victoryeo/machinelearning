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

recipe_cost = 0
recipes={} # to store name of the recipe
prices={} # to store price of the recipe
driver.get("https://food.mthai.com/food-recipe")

# convert a string quotient to float
def convert(s):
    try:
        return float(s)
    except ValueError:
        try:
            num, denom = s.split('/')
            return float(num) / float(denom)
        except ValueError:    
            return 0;
    
# price list
GLUTINOUS_RICE_FLOUR = 10   # THB per 1g 
GRATED_COCONUT = 5          # THB per 1g 
PALM_SUGAR = 2              # THB per 1g
def checkPrice(item, amountname, unitname):
    cost  = 100
    unit = 1
    print(item, amountname, unitname)
    amount = convert(amountname)
    
    if (unitname == 'กิโล' or unitname == 'กิโลกรัม'):
        unit = 1000
    elif (unitname == 'กรัม'): 
        unit = 1
    elif (unitname == 'ช้อนชา'):
        unit = 1
    elif (unitname == 'ช้อนโต๊ะ'):
        unit = 1
    elif (unitname ==  "ถ้วย"):
        unit = 1
    elif (unitname ==  "ถ้วยตวง"):
        unit = 1      
    elif (unitname ==  "ฟอง"):
        unit = 1
        
    if (item == 'แป้งข้าวเหนียว'):
        cost = GLUTINOUS_RICE_FLOUR * amount * unit
    elif (item == 'มะพร้าวขูด'):
        cost = GRATED_COCONUT * amount * unit
    elif (item == 'น้ำตาลปี๊บ'):
        cost = GRATED_COCONUT * amount * unit        
    return cost

content = driver.page_source
soup = BeautifulSoup(content)

# process the page content
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
            recipe_cost = 0  # reset cost to zero for each recipe
            ingredients = (tditem.find_next_sibling("ul"))
            #print(ingre)
            ingreditem = ingredients.find_all('li')
            recipes[index]['ingred'] = {}
            for jndex, listitem in enumerate(ingreditem):
                #print(listitem.text)
                split_item = (re.split("( )",listitem.text))
                print(split_item)
                try:
                    recipe_cost += checkPrice(split_item[0], split_item[2], split_item[4])
                except IndexError:
                    recipe_cost += 0
                recipes[index]['ingred'][jndex] = listitem.text
            recipes[index]['cost'] = recipe_cost

recipe_output = []
# loop thru recipes
for k,v in recipes.items():
    #print(k,v)
    for i, (k2,v2) in enumerate(v.items()):
        print(i, k2,v2)
        if k2 == 'title':
            title = v2
        if k2 == 'cost': 
            recipe_output.append({title:v2})
            
# write to csv file
user_ids = []
frames = []
for user_id, d in recipes.items():
    user_ids.append(user_id)
    frames.append(pd.DataFrame.from_dict(d, orient='index'))
    
pd.concat(frames, keys=user_ids).to_csv('/home/vic/workspace/recipes.csv', index=True, encoding='utf-8')
    
#df = pd.DataFrame({'Recipe Name':recipes,'Price':prices}) 
#df.to_csv('/home/vic/workspace/recipes.csv', index=False, encoding='utf-8')