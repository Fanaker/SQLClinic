from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.staticfiles import StaticFiles
from .benchmark import CASES,run_case,run_all
from tools.seed import seed,connect
ROOT=Path(__file__).resolve().parents[1]
app=FastAPI(title='SQL Clinic API',version='1.0.0')
cache={}
@app.on_event('startup')
def initialize():
 seed()
 if not cache:
  for k in CASES:
   cache[k]=run_case(k)
@app.get('/api/overview')
def overview():
 with connect() as c:
  rowcounts={key:c.execute(f'SELECT COUNT(*) FROM {key}').fetchone()[0] for key in ['orders','order_items','customers','products','stores']}
  db_bytes=(ROOT/'data'/'sqlclinic.sqlite3').stat().st_size
 return {'cases':list(cache.values()),'rowcounts':rowcounts,'db_bytes':db_bytes,'engine':'SQLite 3 · local demo','status':'Ready'}
@app.get('/api/cases')
def cases():return [{'id':k,'label':c['label'],'category':c['category'],'problem':c['problem'],'query':c['sql'],'index':c['index']} for k,c in CASES.items()]
@app.post('/api/benchmark/{key}')
def benchmark(key:str):
 if key not in CASES:raise HTTPException(status_code=404,detail='Caso no encontrado')
 cache[key]=run_case(key)
 return cache[key]
@app.get('/api/schema')
def schema():
 with connect() as c:
  return [{'table':table,'columns':[dict(p) for p in c.execute(f'PRAGMA table_info({table})')],'rows':c.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]} for table in ['orders','order_items','customers','products','stores']]
@app.get('/api/health')
def health():return {'status':'ok'}
app.mount('/',StaticFiles(directory=ROOT/'frontend',html=True),name='frontend')
