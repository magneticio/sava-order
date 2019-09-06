from fastapi import FastAPI
from datetime import datetime
from typing import List
from pydantic import BaseModel
import os
from elasticsearch import Elasticsearch


class Basket(BaseModel):
    currency: str
    deviceType: str = None
    itemIds: List[int] = []
    locale: str
    paymentId: str = None
    requestUserAgent: str
    timestamp: datetime = None
    totalItems: int
    totalPrice: float


ES_URL = os.environ['ELASTICSEARCH_URL']
print(f'ELASTICSEARCH_URL: {ES_URL}')
ES_INDEX_NAME = os.environ['ELASTICSEARCH_INDEX_NAME']
print(f'ELASTICSEARCH_INDEX_NAME: {ES_INDEX_NAME}')

es = Elasticsearch([ES_URL])
es.indices.create(index=ES_INDEX_NAME, ignore=400)


app = FastAPI()


@app.post("/basket/")
async def create_basket(basket: Basket):
    basket.timestamp = datetime.now()

    r = es.index(index=ES_INDEX_NAME, body=basket.dict())
    basket.paymentId = r['_id']
    
    return basket.dict()

