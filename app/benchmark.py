"""Execute real SQLite EXPLAIN QUERY PLAN and timings before/after indexes.

PostgreSQL-specific EXPLAIN ANALYZE lives in tools/benchmark_postgres.py.
No fabricated benchmark metrics are included.
"""
from __future__ import annotations
import sqlite3,statistics,time
from datetime import datetime
from pathlib import Path
from tools.seed import connect,seed,DB

CASES={
 'date_range':{'label':'Filtro por rango de fechas','category':'SARGability','problem':'Full table scan para filtrar pedidos por período.','index':'CREATE INDEX idx_orders_date ON orders(placed_at)','sql':'SELECT COUNT(*), ROUND(SUM(total),2) FROM orders WHERE placed_at >= ? AND placed_at < ?','params':['2026-08-01','2026-09-01'],'explain':'Índice B-tree por fecha; el motor evita recorrer toda la tabla.'},
 'customer':{'label':'Historial por cliente','category':'Índices compuestos','problem':'Búsqueda de operaciones de un cliente sin acceso selectivo.','index':'CREATE INDEX idx_orders_customer_date ON orders(customer_id,placed_at)','sql':'SELECT id,placed_at,total FROM orders WHERE customer_id = ? ORDER BY placed_at DESC LIMIT 100','params':[1373],'explain':'El índice compuesto satisface el filtro y el ordenamiento.'},
 'store':{'label':'Ventas por sucursal','category':'Búsqueda selectiva','problem':'Reportes operativos sin índice por sucursal y fecha.','index':'CREATE INDEX idx_orders_store_date ON orders(store_id,placed_at)','sql':'SELECT COUNT(*),ROUND(SUM(total),2) FROM orders WHERE store_id = ? AND placed_at BETWEEN ? AND ?','params':[7,'2026-01-01','2026-12-31'],'explain':'Acceso selectivo a la sucursal, limitado por fechas.'},
 'product':{'label':'Movimientos por producto','category':'Consultas de joins','problem':'Los movimientos de un producto requieren revisar todos los ítems.','index':'CREATE INDEX idx_items_product ON order_items(product_id)','sql':'SELECT COUNT(*),ROUND(SUM(quantity*unit_price),2) FROM order_items WHERE product_id = ?','params':[42],'explain':'Índice sobre la clave de búsqueda en el detalle de líneas.'}
}

CURRENT=Path(__file__).resolve().parents[1]/'data'/'benchmarks.json'

def get_plan(c,query,params):return [row[3] for row in c.execute('EXPLAIN QUERY PLAN '+query,params).fetchall()]
def median_ms(c,query,params,repetitions=9):
 results=[]
 for _ in range(repetitions):
  t=time.perf_counter_ns();c.execute(query,params).fetchall();results.append((time.perf_counter_ns()-t)/1_000_000)
 return round(statistics.median(results),4)

def run_case(key):
 if key not in CASES:raise KeyError(key)
 seed()
 case=CASES[key];index_name=case['index'].split()[2];sql=case['sql'];params=case['params']
 with connect() as c:
  c.execute('DROP INDEX IF EXISTS '+index_name);c.commit()
  # Warm up to avoid interpreting a cold file-system cache as the effect of the index.
  c.execute(sql,params).fetchall()
  before=median_ms(c,sql,params);pre=get_plan(c,sql,params)
  c.execute(case['index']);c.commit();c.execute(sql,params).fetchall()
  after=median_ms(c,sql,params);post=get_plan(c,sql,params)
  result={'id':key,'label':case['label'],'category':case['category'],'problem':case['problem'],'index':case['index'],'query':sql,'params':params,'before_ms':before,'after_ms':after,'speedup':round(before/max(after,.0001),2),'before_plan':pre,'after_plan':post,'rows':c.execute('SELECT COUNT(*) FROM orders').fetchone()[0],'timestamp':datetime.now().isoformat(timespec='seconds'),'engine':'SQLite 3 (demostración local)'}
 return result

def run_all():return [run_case(key) for key in CASES]

if __name__=='__main__':
 for obj in run_all():print(obj['label'],obj['before_ms'],obj['after_ms'],obj['speedup'])
