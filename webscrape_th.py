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
from matplotlib import pyplot
from statsmodels.tsa.vector_ar.var_model import VAR
import statsmodels.api as sm
import numpy as np

driver = webdriver.Chrome("/home/vic/workspace/chromedriver")

recipe_cost = 0
recipes={}  # to store name of the recipe
prices={}   # to store price of the recipe

# get the main recipe page
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
            try: 
                #handle this case 1/2ถ้วย
                newdenom = re.findall(r'\d+', denom)
                return float(num) / float(newdenom[0])   
            except:
                return 0          
    
def getEnglishName(item):
    englishitem = 'none'
    if (item == 'แป้งข้าวเหนียว' or item == 'แป้งเค้ก'):    
        englishitem = 'FLOUR'
    elif (item == 'มะพร้าวขูด'):
        englishitem = 'GRATED_COCONUT'
    elif (item == 'น้ำตาลปี๊บ' or item == 'น้ำตาลทราย'):
        englishitem = 'SUGAR'      
    elif (item == 'ไข่เป็ด'):
        englishitem = 'DUCK_EGG'              
    elif (item == 'เกลือ'):
        englishitem = 'SALT'
    elif (item == 'มันกุ้ง' or item == 'กุ้งสด' or item == 'กุ้ง(ลวก)'):
        englishitem = 'SHRIMP'    
    elif (item == 'แป้งสาลี'):
        englishitem = 'DOUGH'           
    elif (item == 'ยีสต์'):
        englishitem = 'YEAST'
    elif (item == 'น้ำอุ่น' or item == 'น้ำ'):
        englishitem = 'WATER'
    elif (item == 'กระเทียมสับ' or item == 'กระเทียม'):
        englishitem = 'GARLIC'
    elif (item == 'ข้าวสวย'):
        englishitem = 'RICE'
    return englishitem
        
# price list
FLOUR = 10                  # THB per 1g 
GRATED_COCONUT = 5          # THB per 1g 
SUGAR = 2                   # THB per 1g
DUCK_EGG = 10               # THB per 1 piece
SALT = 7                    # THB per 1g
SHRIMP = 30                 # THB per 1g
DOUGH = 5
YEAST = 9                   # per tablespoon
WATER = 1
GARLIC = 8
RICE = 3
def checkPrice(item, amountname, unitname):
    cost  = 10
    unit = 1
    print(item, amountname, unitname)
    amount = convert(amountname)
    
    if (unitname == 'กิโล' or unitname == 'กิโลกรัม'):
        unit = 1000
    elif (unitname == 'กรัม'): 
        unit = 1
    elif (unitname == 'ช้อนชา'):    #teaspoon
        unit = 1
    elif (unitname == 'ช้อนโต๊ะ'):    #tablespoon
        unit = 2
    elif (unitname ==  "ถ้วย"):       #cup
        unit = 1
    elif (unitname ==  "ถ้วยตวง"):  #measure cup
        unit = 1      
    elif (unitname ==  "ฟอง"):      #bubble
        unit = 1
        
    if (item == 'แป้งข้าวเหนียว' or item == 'แป้งเค้ก'):
        cost = FLOUR * amount * unit
    elif (item == 'มะพร้าวขูด'):
        cost = GRATED_COCONUT * amount * unit
    elif (item == 'น้ำตาลปี๊บ' or item == 'น้ำตาลทราย'):
        cost = SUGAR * amount * unit      
    elif (item == 'ไข่เป็ด'):
        cost = DUCK_EGG * amount * unit             
    elif (item == 'เกลือ'):
        cost = SALT * amount * unit  
    elif (item == 'มันกุ้ง' or item == 'กุ้งสด' or item == 'กุ้ง(ลวก)'):
        cost = SHRIMP * amount * unit   
    elif (item == 'แป้งสาลี'):
        cost = DOUGH * amount * unit   
    elif (item == 'ยีสต์'):
        cost = YEAST * amount * unit 
    elif (item == 'น้ำอุ่น' or item == 'น้ำ'):
        cost = WATER * amount * unit 
    elif (item == 'กระเทียมสับ' or item == 'กระเทียม'):
        cost = GARLIC * amount * unit    
    elif (item == 'ข้าวสวย'):
        cost = RICE * amount * unit                   
        
    return cost

# retrieve the page content
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
            recipes[index]['ingred_english'] = {}
            for jndex, listitem in enumerate(ingreditem):
                #print(listitem.text)
                split_item = (re.split("( )",listitem.text))
                print(split_item)
                #handle this case แครอท (ซอย) 2 ช้อนโต๊ะ
                try:
                    if split_item[2].isdecimal() == False:
                        split_item[0] = split_item[0] + split_item[2]
                        split_item[2] = split_item[4]
                        split_item[4] = split_item[6]
                except IndexError:
                    split_item[0] = split_item[0]
                try:
                    recipe_cost += checkPrice(split_item[0], split_item[2], split_item[4])
                except IndexError:
                    recipe_cost += 0
                recipes[index]['ingred'][jndex] = listitem.text
                try:
                    english_name = getEnglishName(split_item[0])
                    if  english_name in recipes[index]['ingred']:
                      recipes[index]['ingred_english'][english_name] += convert(split_item[2])               
                    else:
                      recipes[index]['ingred_english'][english_name] = convert(split_item[2])               
                except IndexError:
                    recipes[index]['ingred_english'][english_name] = 0
            recipes[index]['cost'] = recipe_cost

recipe_output = []
# loop thru recipes
for k,v in recipes.items():
    #print(k,v)
    for i, (k2,v2) in enumerate(v.items()):
        print(i, k2,v2)
        if k2 == 'title':
            title = v2
        #if k2 == 'ingred':
        #    recipe_output.append({})
        if k2 == 'cost': 
            recipe_output.append({title:v2})
            
# write to csv file
user_ids = []
frames = []
for user_id, d in recipes.items():
    user_ids.append(user_id)
    frames.append(pd.DataFrame.from_dict(d, orient='index'))
    
pd.concat(frames, keys=user_ids).to_csv('/home/vic/workspace/recipes.csv', index=True, encoding='utf-8')

# read from food price
fooddataset = pd.read_csv('/home/vic/workspace/food_prices.csv', header=0, parse_dates=[0], index_col=0)
food_price = fooddataset.iloc[:, 1:7].values
print(fooddataset.head())    
fooddataset.plot()
pyplot.show()

# build forecast model
X = fooddataset.values
history = [x for x in X]
model = VAR(endog=X)
model_fit = model.fit()
prediction = model_fit.forecast(model_fit.y, steps=1)

# forecast by using menu name
menu_name = 'สูตรขนมไหว้เจ้าในวันตรุษจีน'
# search the recipes
for k,v in recipes.items():
    for i, (k2,v2) in enumerate(v.items()):
        if k2 == 'title':
            if menu_name in v2:
                print("matched")
                match = k
                break
            
def getPosition(argument): 
    switcher = { 
        'DOUGH': 5, 
        'SALT': 0, 
        'SUGAR': 1, 
        'YEAST': 6,
        'SHRIMP': 4,
        'COCONUT': 3,
        'DUCK_EGG': 2
    } 
    return switcher.get(argument, 0) 
 
# build the ingredient based on menu name    
ingredient_dict = {0: 0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
#print(recipes[match]['ingred_english'])
for k3,v3 in recipes[match]['ingred_english'].items():
    pos = getPosition(k3)
    print (pos, k3,v3)
    ingredient_dict[pos] = v3

#XX =np.array(list(ingredient_dict.items()))
#XX = np.array([0,0,0,0,0,0,0])
XX =  np.empty((0,6), float)
for (k4,v4) in ingredient_dict.items():
    XX = np.append(XX, v4)    

# make prediction using the model built earlier
# based on the data from the menu name
XX = np.append(XX, XX, axis=0)
B = np.reshape(XX, (-1, 7)) 
prediction = model_fit.forecast(B, steps=1)

# sum up the food cost
predicted_cost =  np.sum(prediction)
print('The predicted food cost for', menu_name ,'menu is ' , predicted_cost)
