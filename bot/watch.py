import asyncio
import pymongo
from base_logger import logger
from data import api
from pymongo import MongoClient

client = MongoClient()
db = client.ilo

async def watch():
    with db.playoffs.watch(
            [{'$match': {'operationType': 'insert'}}]) as stream:
        for insert_change in stream:
            print(insert_change)
    
    
async def main():    
    task_1 = asyncio.create_task(
        watch()
    )

asyncio.run(main())
