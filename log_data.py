from typing import Annotated
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

import pandas as pd
import plotly
import plotly.express as px
import json

import math

import sqlite3
import datetime

app = FastAPI(
    title="EFI Development",
    openapi_url=f"/openapi.json",
    docs_url=f"/docs",
    redoc_url=f"/redoc",
    root_path="/tunnel_rachcai" # <------ root_path adjustment fixes the prepend on the tunnel
)

def compute_heat_index(rh, t):
    hi = (-42.379 
          + 2.04901523 * t 
          + 10.14333127 * rh 
          - 0.22475541 * t * rh 
          - 0.00683783 * t * t 
          - 0.05481717 * rh * rh 
          + 0.00122874 * t * t * rh 
          + 0.00085282 * t * rh * rh 
          - 0.00000199 * t * t * rh * rh)

    if rh < 13 and 80 <= t <= 112:
        adjustment = ((13 - rh) / 4) * math.sqrt((17 - abs(t - 95)) / 17)
        hi -= adjustment
    elif rh > 85 and 80 <= t <= 87:
        adjustment = ((rh - 85) / 10) * ((87 - t) / 5)
        hi += adjustment

    return round(hi)

EX_DB = "rachcai_test/ex1_log.db"

@app.post("/logger")
async def log_data(temp: float, rh: float, kerberos: str, bat: float):
    heat_index = compute_heat_index(rh, temp)
    timing = datetime.datetime.now()
    conn = sqlite3.connect(EX_DB)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS rht_table (kerberos real, rh real, t real, heat_index real, bat real, timing timestamp);''')
    
    c.execute('''INSERT INTO rht_table (kerberos, rh, t, heat_index, bat, timing) VALUES (?, ?, ?, ?, ?, ?);''',
              (kerberos, rh, temp, heat_index, bat, timing))
    
    conn.commit()
    conn.close()
    return("data posted")
    
@app.get("/getter")
async def root(kerb: str, time: int):
    conn = sqlite3.connect(EX_DB)
    c = conn.cursor()

    cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=time)
    c.execute('''SELECT timing, t, rh, heat_index, bat FROM rht_table WHERE timing >= ?''', (cutoff_time,))
    
    results = c.fetchall()
    conn.close()

    data = [{"time": row[0], "temp": row[1], "humidity": row[2], "heat_index": row[3], "battery": row[4]} for row in results]
    return {"data": data}