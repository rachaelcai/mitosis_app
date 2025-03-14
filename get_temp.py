from typing import Annotated
from fastapi import FastAPI, Query
import math

import sqlite3
import datetime

# app = FastAPI()

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

@app.get("/heat_index")
async def root(rh: float, t: float):
    return compute_heat_index(rh, t)

RHT_DB = "rachcai_test/rht_log.db"
@app.get("/heat_index2")
def heat_index_function2(rh: float, t: float, history: int | None = None):
    heat_index = compute_heat_index(rh, t)
    timing = datetime.datetime.now()
    conn = sqlite3.connect(RHT_DB)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS rht_table (rh real, t real, heat_index real, timing timestamp);''')
    
    c.execute('''INSERT INTO rht_table (rh, t, heat_index, timing) VALUES (?, ?, ?, ?);''',
              (rh, t, heat_index, timing))
    
    if history is not None:
        cutoff_time = timing - datetime.timedelta(seconds=history)
        prev_data = c.execute('''SELECT rh, t, heat_index FROM rht_table WHERE timing >= ? ORDER BY timing DESC;''', (cutoff_time,)).fetchall()
    else:
        prev_data = c.execute('''SELECT rh, t, heat_index FROM rht_table ORDER BY timing DESC;''').fetchall()
    
    conn.commit()
    conn.close()
    
    outs = ""
    for t in prev_data:
        outs += f"rh: {t[0]} t: {t[1]} heat_index: {t[2]}! "
     
    return outs

EX_DB = "rachcai_test/ex1_log.db"

@app.post("/efi_test/logger")
async def log_data(temp: float, rh: float, kerberos: str, bat: float):
    heat_index = compute_heat_index(rh, temp)
    timing = datetime.datetime.now()
    conn = sqlite3.connect(EX_DB)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS rht_table (kerberos real, rh real, t real, heat_index real, bat real, timing timestamp);''')
    
    c.execute('''INSERT INTO rht_table (kerb, rh, t, heat_index, timing) VALUES (?, ?, ?, ?, ?, ?);''',
              (kerberos, rh, t, heat_index, bat, timing))
    



