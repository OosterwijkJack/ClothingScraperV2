import json
import sqlite3


conn = sqlite3.connect("../Website/clothes.db")
cursor = conn.cursor()

def searchJson(jsonData):
    print(jsonData["data"]["search2"]["nextPageId"])

def main():
    f = open("data.out", "r")
    data = f.read()
    jsonData = json.loads(data)
    f.close()

    exactCount = safe_get(jsonData, "data", "search2", "exactCount")
    partialCount = safe_get(jsonData, "data", "search2", "partialCount")
    realCount = exactCount if exactCount else partialCount
    
    nextPageId = jsonData["data"]["search2"]["nextPageId"]

    results = jsonData["data"]["search2"]["results"]
    for i in results:
        
        product = i["product"]
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
            "nextPageId": nextPageId,
            "count": realCount
        }
        print(product_data)
        exit()
        #insertClothes(product_data)

def insertClothes(data):
    try:
        sql = """
    INSERT INTO clothes (link, img_link, description, price)
    VALUES (:link, :image_link, :description, :price)
        """
        cursor.execute(sql, data)
        conn.commit()
    except Exception as e:
        print(e)

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

main()