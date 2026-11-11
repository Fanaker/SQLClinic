"""Generate a fully reproducible retail database for benchmarking."""
from __future__ import annotations
import random,sqlite3,time
from pathlib import Path
from datetime import date,timedelta
ROOT=Path(__file__).resolve().parents[1];DB=ROOT/'data'/'sqlclinic.sqlite3'
SCHEMA='''
CREATE TABLE IF NOT EXISTS stores(id INTEGER PRIMARY KEY,name TEXT NOT NULL,region TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS customers(id INTEGER PRIMARY KEY,segment TEXT NOT NULL,city TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY,name TEXT NOT NULL,category TEXT NOT NULL,price REAL NOT NULL);
CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY,customer_id INTEGER NOT NULL,store_id INTEGER NOT NULL,placed_at TEXT NOT NULL,status TEXT NOT NULL,total REAL NOT NULL);
CREATE TABLE IF NOT EXISTS order_items(id INTEGER PRIMARY KEY,order_id INTEGER NOT NULL,product_id INTEGER NOT NULL,quantity INTEGER NOT NULL,unit_price REAL NOT NULL);
'''
ROWS=50000

def connect():
 DB.parent.mkdir(parents=True,exist_ok=True)
 con=sqlite3.connect(DB,timeout=30);con.row_factory=sqlite3.Row;con.executescript(SCHEMA);return con

def seed(force=False):
 if force and DB.exists():DB.unlink()
 with connect() as c:
  count=c.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
  if count>=ROWS:return count
  r=random.Random(202610)
  c.executemany('INSERT INTO stores VALUES(?,?,?)',[(i,f'Sucursal {i:02d}',r.choice(['Lima Centro','Lima Norte','Lima Sur','Callao'])) for i in range(1,25)])
  c.executemany('INSERT INTO customers VALUES(?,?,?)',[(i,r.choice(['Minorista','Corporativo','Frecuente']),r.choice(['Lima','Arequipa','Trujillo','Piura'])) for i in range(1,4001)])
  c.executemany('INSERT INTO products VALUES(?,?,?,?)',[(i,f'Producto {i:03d}',r.choice(['Hogar','Abarrotes','Bebidas','Limpieza']),r.randint(5,160)) for i in range(1,101)])
  origin=date(2024,1,1);rows=[];items=[];item_id=1
  for i in range(1,ROWS+1):
   customer=r.randint(1,4000);store=r.randint(1,24);when=(origin+timedelta(days=r.randrange(1020))).isoformat();status=r.choice(['Completado']*8+['Pendiente','Cancelado']);value=round(r.uniform(20,500),2)
   rows.append((i,customer,store,when,status,value))
   for j in range(r.randint(1,3)):
    items.append((item_id,i,r.randint(1,100),r.randint(1,5),round(value/(j+2),2)));item_id+=1
  c.executemany('INSERT INTO orders(id,customer_id,store_id,placed_at,status,total) VALUES(?,?,?,?,?,?)',rows)
  c.executemany('INSERT INTO order_items VALUES(?,?,?,?,?)',items)
 return ROWS
if __name__=='__main__':
 print('Seeded',seed(),'orders')
