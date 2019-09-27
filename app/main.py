from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import List
from pydantic import BaseModel
import os
from elasticsearch import Elasticsearch
import logging


class Basket(BaseModel):
    currency: str
    deviceType: str = None
    itemIds: List[int]
    locale: str
    paymentId: str = None
    requestUserAgent: str
    timestamp: datetime = None
    totalItems: int
    totalPrice: float


logger = logging.getLogger("app")
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

log_level = os.getenv('LOG_LEVEL')
if log_level:
    log_level = log_level.lower()
    if log_level == 'debug':
        logging.basicConfig(level=logging.DEBUG)
    elif log_level == 'info':
        logging.basicConfig(level=logging.INFO)
    elif log_level == 'warning':
        logging.basicConfig(level=logging.WARNING)
    elif log_level == 'error':
        logging.basicConfig(level=logging.ERROR)
    elif log_level == 'critical':
        logging.basicConfig(level=logging.CRITICAL)
    else:
        logger.warning(f'Unknown LOG_LEVEL value: {log_level}')

# crash if not set
ES_URL = os.environ['ELASTICSEARCH_URL']
logger.info(f'ELASTICSEARCH_URL: {ES_URL}')

# crash if not set
ES_INDEX_NAME = os.environ['ELASTICSEARCH_INDEX_NAME']
logger.info(f'ELASTICSEARCH_INDEX_NAME: {ES_INDEX_NAME}')

es = Elasticsearch([ES_URL])
if not es.indices.exists(ES_INDEX_NAME):
    es.indices.create(index=ES_INDEX_NAME, ignore=400)

app = FastAPI()


@app.post("/basket/")
async def create_basket(basket: Basket):
    basket.timestamp = datetime.now()

    r = es.index(index=ES_INDEX_NAME, body=basket.dict())
    basket.paymentId = r['_id']
    
    return basket.dict()

@app.get("/ready/")
async def ready():
    if not es.indices.exists(ES_INDEX_NAME):
        raise HTTPException(status_code=418, detail=f'Elasticsearch index {ES_INDEX_NAME} unavailable')

    return {'ready': True}

