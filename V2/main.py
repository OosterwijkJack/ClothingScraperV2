import request_data
import requests
import json
import sqlite3
import time
import os
from datetime import date, timedelta, datetime, timezone
from urllib.parse import quote

conn = sqlite3.connect("../Website/clothes.db")
cursor = conn.cursor()

total_count = 0
total_finds = 0
total_scans = 0

COUNT = 100

GLOBAL_EXCLUDE = []
errors_history = []

def main():
    global total_count, GLOBAL_EXCLUDE

    f = open("../rules.json", "r", encoding="utf-8")
    rules = json.load(f) 
    f.close()

    brands = rules["brands"] # get rules for specific brand
    GLOBAL_EXCLUDE = rules["GLOBAL_EXCLUDE"]
    realCount = 0
    for brand in brands:
        date_last_checked = getRecentDate(brand)
        total_count = 0
        brand_rules = rules[brand]

        variables  = { # search query
            "query": {"terms":brand,"addedAfter":date_last_checked, "gender": "m"},
            "count": COUNT,
        }
        response = requests.post(request_data.url, headers=request_data.headers, cookies=request_data.cookies, 
                                json= request_data.createPayload(variables))
        dataJson = response.json()
        #print(dataJson)
        # total count of how many items matched the query
        exactCount = safe_get(dataJson, "data", "search2", "exactCount")
        #partialCount = safe_get(dataJson, "data", "search2", "partialCount")
        realCount = exactCount

        nextPageId = dataJson["data"]["search2"]["nextPageId"]

        process_request(dataJson, brand_rules) # process the initial request

        while total_count < realCount: # loop until all items from query are processed 
            time.sleep(0.25)
            # repeat process but use the nextPageId
            variables  = { # search query
            "query": {"terms":brand,"addedAfter":f"{date_last_checked}", "gender": "m"},
            "count":COUNT,
            "nextPageId": nextPageId,
            
            } 
            response = requests.post(request_data.url, headers=request_data.headers, cookies=request_data.cookies, 
                                json= request_data.createPayload(variables))
            dataJson = response.json()
            try:
                nextPageId = dataJson["data"]["search2"]["nextPageId"] # get next page id again
            except Exception:
                print(dataJson)
                exit()
            if(not nextPageId):
                break
            process_request(dataJson, brand_rules)
        


def displayProgress(brand, count):
    global total_count, total_finds, total_scans
    percent = 0
    if count != 0:
        percent = float(total_count / count) * 100
    print(f"{brand}: {total_count}/{count} ({percent:.2f}%)" if brand else "")   
    print(f"Total finds: {total_finds}/{total_scans}")

def process_request(jsonData, rules):
    global total_count, total_scans
    results = jsonData["data"]["search2"]["results"]

    for item in results:
        total_count += 1
        total_scans += 1
        product = item["product"]
        price_float = float(product["price"].replace("CA$", "").replace(",", ""))

        product_data = {
            "link": product.get("url", ""),
            "source": product.get("source", ""),
            "description": product.get("title", ""),
            "price": price_float,
            "originating_country": product.get("countryName", ""),
            "image_link": safe_get(product, "images", 0, "thumbnail", "url"),
            "id": product.get("id", ""),
            "sizeParam": safe_get(product, "sizesV1", 0, "values", 0, "sizeParam"),
            "isAuction": product.get("isAuction", ""),
        }
        if(filterRules(rules, product_data["description"], price_float)):
            insertClothes(product_data)

def safe_get(obj, *keys, default=""):
    """Safely get nested dictionary values."""
    try:
        for key in keys:
            if isinstance(obj, list):
                obj = obj[key] if obj else default
            else:
                obj = obj.get(key, default)
            if obj == default:
                return default
        return obj
    except (KeyError, IndexError, TypeError, AttributeError):
        return default
    

def insertClothes(data):
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

def filterRules(rules, desc, price):
    global GLOBAL_EXCLUDE
    returnValue = False
    default = True

    # filter out items with excluded keyword

    for i in GLOBAL_EXCLUDE: 
        if i in desc.lower():
            return False 
    for i in rules["exclude"]: # rules that only pertain to this brand
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

def getRecentDate(brand):
    toReturn = ""
    sql = f"""
SELECT * FROM results WHERE ID = '{brand}'
"""
    cursor.execute(sql)
    result = cursor.fetchall()

    now = datetime.now(timezone.utc)
    iso_time = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    if(result[0][1] != None):
        toReturn = (result[0][1])
    else:
        # generate new date 
        toReturn = iso_time
    
    sql = f"""
UPDATE results
SET last_checked = '{iso_time}'
WHERE ID = '{brand}'
"""
    cursor.execute(sql)
    conn.commit()
    return toReturn

main()