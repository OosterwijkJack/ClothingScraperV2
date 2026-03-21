headers = {
    "Host": "jpfans.com",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "From-Source-Type": "PC",
    "Content-Length": "329",
    "Origin": "https://jpfans.com",
    "Connection": "keep-alive",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}
def get_payload(page, brands):
    return {"platform":"mercari",
            "cacheDisabled":False,
            "category":["2"],"keyword":"",
            "excludeKeyword":"","itemTypes":[],
            "brands":brands,"productCondition":[],
            "sizes":[],"priceMin":0,
            "priceMax":0,
            "shippingCost":[],
            "colors":[],
            "page":page,
            "pageSize":40,
            "sort":"2", # newest sort
            "shopId":"",
            "userId":"",
            "translateKeywords":False,
            "lang":"en",
            "language":"en"}
