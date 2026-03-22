import json
import requests
import jp_data
from forex_python.converter import CurrencyRates
import sqlite3
import time

cRates = CurrencyRates()
JPYtoCAD = cRates.get_rate("JPY", "CAD")

conn = sqlite3.connect("../../Website/clothes.db")
cursor = conn.cursor()

url = "https://jpfans.com/search-info/search?lang=en&language=en&wmc-currency=CAD"
total_finds = 0

GLOBAL_EXCLUDE = []

DUP_MAX = 3
def main():
    global GLOBAL_EXCLUDE
    f = open("../../rules.json")
    rules = json.load(f)
    f.close()

    GLOBAL_EXCLUDE = rules["GLOBAL_EXCLUDE"] 
    tmpp = False
    
    for i in rules["brands"]:

        if(len(rules[i]["id"]) <= 0): # if the brand has an id
            continue

        print(i) # print brand name
        page = 1
        dup = 0

        discoveredDuplicate = False

        while True:
            if dup >= DUP_MAX:
                break

            response = requests.post(url, json=jp_data.get_payload(page, rules[i]["id"]), headers=jp_data.headers)
            try:
                data = json.loads(response.text)
            except Exception as e:
                print(e)
                print(response.text)

            if len(data["data"]["items"]) <= 0:
                print("REACHED END")
                break

            for j in data["data"]["items"]:
                price = round(int(j["price"]) * JPYtoCAD, 2)
                desc = j["nameI18n"]
                image_link = j["image"]
                id = j["id"]
                link = f"https://jpfans.com/product?id={id}&platform=mercari"
                instertDict = {"link": link, "image_link": image_link, "description": desc, "price": price}

                if(filterRules(rules[i], desc, price)):
                    if insertClothes(instertDict): # returns true when duplicate
                        dup+= 1
                    else:
                        dup = 0
            time.sleep(0.1)
            page += 1

def insertClothes(data) -> bool:
    global total_finds
    try:
        sql = """
    INSERT INTO clothes (link, img_link, description, price, seen)
    VALUES (:link, :image_link, :description, :price, 0)
        """
        cursor.execute(sql, data)
        conn.commit()
        total_finds += 1
        print(f"Found: {data["description"]} | total finds: {total_finds}")
    except Exception as e:
        if "UNIQUE" not in str(e):
            print(e)
        else:
            print("DUPLICATE")
            return True # duplicate 
        
def filterRules(rules, desc, price):
    global GLOBAL_EXCLUDE
    returnValue = False
    default = True

    # filter out items with excluded keyword

    for i in GLOBAL_EXCLUDE:
        if i in desc.lower():
            return False 
    

    # price filter
    for key, max_price in rules["price"].items():
        if (key.lower()) in desc.lower():
            default = False

            if (price) < max_price: # approximate USD conversion change to be updated later
                return True
    # defaul price thereshold
    if default and price < rules["price"]["default"]:
        returnValue = True
    
    return returnValue


main()

