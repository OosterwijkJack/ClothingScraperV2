

url = "https://backend.gem.app/graphql"

headers = {
    "Host": "backend.gem.app",
    "Sec-Ch-Ua-Platform": '"Linux"',
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Not(A:Brand";v="8", "Chromium";v="144"',
    "Content-Type": "application/json",
    "Sec-Ch-Ua-Mobile": "?0",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Origin": "https://gem.app",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://gem.app/",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=1, i"
}

cookies = {
    "currency": "CAD",
    "measurements": "%7B%22mtsUnits%22%3A%22orig%22%2C%22mtsConvertFlat%22%3Anull%7D",
    "homeImage": "15%2C0",
    "sidePanel": "{%22isOpen%22:false}",
    "_ga": "GA1.1.175327028.1770573429",
    "_ga_49N51MV1DX": "GS2.1.s1770573429$o1$g1$t1770573460$j29$l0$h0"
}

def createPayload(variables):
  return {
      "query": """query search2($query: SearchQueryInput!, $nextPageId: String, $count: Int) {
    search2(query: $query, nextPageId: $nextPageId, count: $count) {
      results {
        type
        product {
          ...ProductFragment
        }
      }
      nextPageId
      exactCount
      partialCount
      suggestions
    }
  }

  fragment ProductFragment on Product {
    id
    productId
    source
    url
    urlAffiliate
    available
    removedDate
    seller
    title
    price
    priceOriginalNumber
    priceOriginalCurrency
    gender
    countryName
    images {
      thumbnail {
        url
        width
        height
      }
      full {
        url
        width
        height
      }
    }
    outboundLinkText
    itemTypeV1
    sizesV1 {
      type
      label
      values {
        label
        value
        value2
        unit
        isMore
        sizeParam
        convLabel
        convValue
      }
      notes {
        icon
        text
        action
      }
    }
    isAuction
    saved
  }""",
      "operationName": "search2",
      "variables": variables
  }

