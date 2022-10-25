##LoadBalancer

##IMPORTS
from datetime import datetime
import time
import subprocess

#install aiohttp
import httpx
import asyncio

from fastapi import FastAPI
from pydantic import BaseModel

class Generation(BaseModel):
    inputtext: str
    length: int
    temperature: float
    top_k: int
    top_p: float
    rep_pen: float

class Instance(BaseModel):
    vastID: str
    price: int
    apiURL: float
    gpuName: int
    job: float

app = FastAPI()

class GPUInstance:
    def __init__(self, vastID, price, apiURL, gpuName="RTX A6000", job='text', active=True):
        self.vastID = vastID
        self.price = price
        self.apiURL = apiURL
        #if 'A6000' or '3090' gpu
        self.gpuName = gpuName
        #if 'text' or 'photo' generation
        self.job = job
        #change this depending on number of calls
        self.concurrentApiCalls = 0
        #can we call this instance
        self.active = active

#LIST OF ACTIVE INSTANCES
activeInstances = []

def lowestConcurrentReq(self):
        minInstance = min(activeInstances,key=lambda x:x.concurrentApiCalls)
        return minInstance

@app.post("/list")
async def req2(generation: Generation):
    #USE ROUTE TO SELECT THE INSTANCE URL WE WILL SEND IT TO
    instanceToUse = lowestConcurrentReq()
    #TURN INPUT INTO JSON
    jsoned = generation.dict()
    print(jsoned)
    #SEND ASYNC REQ TO SERVER + RETURN IT TO SENDER
    async with httpx.AsyncClient() as client:
        print(f"SENDING REQ, THIS INSTANCE CURENTLY HAS {instanceToUse.concurrentApiCalls} REQS")
        instanceToUse.concurrentApiCalls = instanceToUse.concurrentApiCalls + 1 
        r = await client.post(f"{instanceToUse.apiURL}/list", json=jsoned, timeout=None)
        data = r.text   
        instanceToUse.concurrentApiCalls = instanceToUse.concurrentApiCalls + - 1
        return data

@app.post("/create_instance")
async def req3(instance: Instance):
    newlycreated = GPUInstance(instance['vastID'], instance['price'], instance['apiURL'], instance['gpuName'])
    print("NEW INSTANCE CREATED")
    activeInstances.append(newlycreated)

