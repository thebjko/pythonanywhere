from imp import reload

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from decimal import Decimal
import urllib.parse
import urllib.request
import json
import re

from secrets import *

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


class Item(BaseModel):
    display: int | None = 45
    keywords: str


@app.post("/search/")
async def search(item: Item):
    x = jsonable_encoder(item)
    # print(x)

    display = str(x["display"])
    query = urllib.parse.quote(x["keywords"])
    start = "1"

    # print(f"display: {display}\nquery: {query}\nstart: {start}")
    url = "https://openapi.naver.com/v1/search/shop.json?query=" + query + "&display=" + display + "&start=" + start
    # print(url)
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)

    response = urllib.request.urlopen(request)

    result = response.read().decode("utf-8")
    converted = json.loads(result)
    items_list = converted["items"]

    json_compatible_item_data = jsonable_encoder(items_list)
    items_list.clear()

    result_list = []
    if len(json_compatible_item_data) != 0:
        for i in json_compatible_item_data:
            title = re.sub("<br>|</br>|<b>|</b>", "", i["title"])
            link = i["link"]
            image_url = i["image"]
            price = "￦ {:,.0f}".format(float(i["lprice"]))
            mall_name = i["mallName"]
            result_list.append({"title": title,
                                "link": link,
                                "imageUrl": image_url,
                                "price": price,
                                "mallName": mall_name})

    return JSONResponse(content=result_list)
