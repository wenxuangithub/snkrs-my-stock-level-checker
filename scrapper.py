import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import pytz
import json
import re

url = "https://www.nike.com/my/launch?s=upcoming"
headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}

itemlist = []
shoe_size = []




def scrap():
  response = requests.get(url,headers=headers)
  soup = BeautifulSoup(response.content, 'html.parser')

  details = soup.find_all("a", class_='ncss-col-sm-8 launch-details u-full-height va-sm-t full')

  skuraw = soup.find_all('img', class_='image-component')

  for item, sku in zip(details, skuraw) :
    link = 'https://www.nike.com'+ item['href']
    name = item.h3.text.strip()
    date = item.find('div', class_='available-date-component').text.strip()

    date_match = re.search(r'(\d{1,2}/\d{1,2})', date)
    time_match = re.search(r'(\d{1,2}:\d{2} [APMapm]{2})', date)
    sku_pattern = r'/([a-zA-Z0-9-]+)-release-date\.jpg$'

    skuid = sku['src']
    match = re.search(sku_pattern, skuid)
    if match:
      sku_id = match.group(1)
      ref = sku_id[:-11]

      if date_match and time_match:
          date = date_match.group(1)
          time = time_match.group(1)

          # Convert the time to UTC+8
          datetime_str = f"{date} {time}"
          datetime_obj = datetime.strptime(datetime_str, "%d/%m %I:%M %p")

          # Assuming UTC is the original timezone of your input
          utc_time = datetime_obj.replace(tzinfo=pytz.utc)
          utc_plus_8_time = utc_time.astimezone(pytz.timezone("Asia/Shanghai"))

          result = {
              "Name": name,
              "Date": date,
              "Time": time,
              "Time (UTC+8)": utc_plus_8_time.strftime("%H:%M %p"),
              'Link': link,
              'Skuid' : (sku_id[-10:]).upper(),
              'Reference' : ref
          }

          itemlist.append(result)

def sizeapi(shoes_ref):
  sizecall = "https://api.nike.com/product_feed/threads/v3/?filter=marketplace%28MY%29&filter=language%28en-GB%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=seoSlugs%28" + shoes_ref + "%29&filter=exclusiveAccess%28true%2Cfalse%29"
  stocklevelurl = requests.get(sizecall, headers=headers)

  data = stocklevelurl.json()

  skus_data = [
    {"nikeSize": sku["nikeSize"],"gtin": sku["gtin"]}
    for product_info in data["objects"][0]["productInfo"]
    for sku in product_info.get("skus", [])
  ]

  # Extract "gtin" and "level" from "availableGtins"
  available_gtins_data = [
    {"gtin": gtin["gtin"], "level": gtin["level"]}
    for product_info in data["objects"][0]["productInfo"]
    for gtin in product_info.get("availableGtins", [])
  ]

    # Combine the information
  combined_data = [
      {
        "gtin": sku["gtin"],
        "nikeSize": sku["nikeSize"],
        "level": gtin["level"]
        }
    for sku in skus_data
    for gtin in available_gtins_data
    if sku["gtin"] == gtin["gtin"]
  ]

  parseData = {
    "productname" : shoes_ref,
    "size" : combined_data }

  # Convert combined_data dictionary outside list
  shoe_size.append(parseData)

if __name__ == "__main__":
    
  scrap()
  sizeapi('NAME') #User required to parse the selected NAME from the itemlist['Reference']


