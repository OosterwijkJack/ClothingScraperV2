from playwright.async_api import async_playwright
import time
import sqlite3
import json
from datetime import date, timedelta
import asyncio
import os
from forex_python.converter import CurrencyRates

conn = sqlite3.connect("Website/clothes.db")
cursor = conn.cursor()

count = 0

SCROLL_BY = "10000"
GLOBAL_EXCLUDE = []

progress_data = {}

cRates = CurrencyRates()
cadToUSD = cRates.get_rate("USD", "CAD")

class Colors:
    GREEN = '\033[92m'
    RST = '\033[0m'

total_finds = 0
async def main():
    async with async_playwright() as p:
        global GLOBAL_EXCLUDE
        # init browser
        browser = await p.chromium.launch(headless=True)
        # read rules file
        f = open("rules.json", "r", encoding="utf-8")
        rules = json.load(f)    

        GLOBAL_EXCLUDE = rules["GLOBAL_EXCLUDE"]

        tasks = []
        task = asyncio.create_task(displayProgress(rules["brands"]))

        tasks.append(task)
        for brand in rules["brands"]:
            context = await browser.new_context()

            # either search through all items or new ones
            if(rules[brand]["limit"] == "new"):

                new_date = getRecentDate(brand) # get last searched date
                
                url = rules[brand]["link"] + f"&addedAfter={new_date}T04%3A59%3A59.999Z"
            elif(rules[brand]["limit"] == "all"): # not actuall all default to a month
                four_weeks_prior = (date.today() - timedelta(days=28)).strftime("%Y-%m-%d")
                url = rules[brand]["link"] + f"&addedAfter={four_weeks_prior}T04%3A59%3A59.999Z"
            
            
            task = asyncio.create_task(searchPage(url, rules[brand], context, brand))
            tasks.append(task)
           

            await asyncio.sleep(3)

        await asyncio.gather(*tasks)
        input("Enter to close ")
        await browser.close()
        cursor.close()

async def displayProgress(brands):

    while True:
        try:
            output = "\033c"  # Build output string first
            all_finished = True
            for i in brands:
                if i not in progress_data.keys():
                    continue
                if progress_data[i]["finished"]:
                    output += f"{Colors.GREEN}{i + ':':<25} {progress_data[i]['complete']}/{progress_data[i]['total']}\n{Colors.RST}"
                else:
                    all_finished = False
                    output += f"{i + ':':<30} {progress_data[i]['complete']}/{progress_data[i]['total']}\n"
                
            # Print in separate thread to avoid blocking
            output += f"\n{"Total Finds:":<30}{total_finds}"
            await asyncio.to_thread(print, output, end="")
            await asyncio.sleep(1)
        except Exception as e:
            print("PRINT ERROR")
            print(e)
   

async def searchPage(url : str, rules : dict, context, brand):
    page = await context.new_page()

    async def close_page():
        await page.close()
        await context.close()

    proccessed_products = []
    await page.goto(url)
    await page.wait_for_load_state("networkidle") # wait for everything to load
    await page.wait_for_timeout(1000)
    
    # get total results for search
    headers = await page.query_selector_all(".header")
    results = []
    for header in headers:
        text = await header.text_content()  # await here
        if "results" in text:
            results.append(header)

    if(len(results) <= 0):
        print("Search FAIL")
        await close_page()
        return
    
    try:
        resultText = await results[0].text_content()
        resultCount = int(resultText.replace(" results", "").replace(",", ""))
    except:
        print("No result or result error")
        await close_page()
        return
    
    
    # collect all results 
    progress_data[brand] = {"total": resultCount, "complete": len(proccessed_products), "finished": False}
    await get_data(page, rules, proccessed_products)
    # loop collecting results until we have collected more than or equal to result count
    while len(proccessed_products) < resultCount:
        await page.evaluate(f"window.scrollBy(0,{SCROLL_BY})")
        await page.wait_for_timeout(150)
        await page.wait_for_load_state("networkidle") # wait for everything to load
        await get_data(page, rules, proccessed_products)
        progress_data[brand] = {"total": resultCount, "complete": len(proccessed_products), "finished": False}
    progress_data[brand] = {"total": resultCount, "complete": len(proccessed_products), "finished": True}  
        
    await close_page()

    


async def get_data(page, rules, proccessed_products) -> bool:
    products = await page.query_selector_all(".productLink") # get results

    for i in products:
        product_id = await getElementID(i)
        product_link = "https://gem.app" + await i.get_attribute("href")

        img = await i.query_selector("img")
        image_link = await img.get_attribute("src")
        product_desc = await img.get_attribute("alt")

        # sometimes may fail but not often enough for it to matter
        try:
            result = await i.query_selector(":scope > .result") # get price of each result
            priceElement = await result.query_selector(":scope > .price")
            priceText = await priceElement.text_content()
            price = float(priceText.replace("$", "").replace(",", "").replace("CA", ""))

            data = {"link": product_link, "image_link": image_link, "description": product_desc, "price": str(price)}

            if product_id not in proccessed_products:
                proccessed_products.append(product_id)
                
                if(filterRules(rules, product_desc, price)):
                   # print(product_desc)
                    insertClothes(data)

        except Exception as e:
            print(f"Erorr: {e}")

async def getElementID(element) -> str:
    return await element.evaluate( # get ID of element to use as key
    """el => {
        if (!el.dataset.uid) {
            el.dataset.uid = crypto.randomUUID();
        }
        return el.dataset.uid;
    }"""
)         

# inserts into clothing table
def insertClothes(data):
    global total_finds
    try:
        sql = """
    INSERT INTO clothes (link, img_link, description, price)
    VALUES (:link, :image_link, :description, :price)
        """
        cursor.execute(sql, data)
        conn.commit()
        total_finds += 1
    except Exception as e:
        print(e)

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

def getRecentDate(brand):
    toReturn = ""
    sql = f"""
SELECT * FROM results WHERE ID = '{brand}'
"""
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if(result[0][1] != None):
        toReturn = (result[0][1])
    else:
        toReturn = date.today().strftime("%Y-%m-%d")
    
    sql = f"""
UPDATE results
SET last_checked = '{(date.today()).strftime("%Y-%m-%d")}'
WHERE ID = '{brand}'
"""
    cursor.execute(sql)
    conn.commit()
    return toReturn


asyncio.run(main())
conn.close()