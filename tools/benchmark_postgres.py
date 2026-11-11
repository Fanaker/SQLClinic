"""Optional live PostgreSQL track. Requires Docker postgres and psycopg[binary].

Creates and populates tables from the reproducible local SQLite dataset, then
executes EXPLAIN (ANALYZE, BUFFERS) on all cases before and after each index.
"""
import os,sqlite3,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.seed import DB,seed
ROOT=Path(__file__).resolve().parents[1]
def main():
 try:import psycopg
 except ImportError:raise SystemExit('Run pip install psycopg[binary]')
 seed();dsn=os.getenv('DATABASE_URL','postgresql://sqlclinic:localdemo@localhost:5435/sqlclinic')
 tables=['stores','customers','products','orders','order_items']
 with psycopg.connect(dsn) as pg,sqlite3.connect(DB) as src:
  with pg.cursor() as c:
   c.execute((ROOT/'sql'/'postgres_schema.sql').read_text())
   for table in tables:
    c.execute(f'TRUNCATE TABLE {table} CASCADE')
   for table in tables:
    columns=[r[1] for r in src.execute(f'PRAGMA table_info({table})')];data=src.execute(f'SELECT * FROM {table}').fetchall()
    placeholders=','.join(['%s']*len(columns))
    # Fast COPY protocol handles hundreds of thousands of rows efficiently.
    with c.copy(f"COPY {table} ({','.join(columns)}) FROM STDIN") as cp:
     for row in data:cp.write_row(row)
   pg.commit()
   print('Imported all SQLite demonstration data into PostgreSQL')
   cases=[('date_range','idx_orders_date','CREATE INDEX idx_orders_date ON orders(placed_at)',"SELECT COUNT(*),SUM(total) FROM orders WHERE placed_at >= DATE '2026-08-01' AND placed_at < DATE '2026-09-01'"),('customer','idx_orders_customer_date','CREATE INDEX idx_orders_customer_date ON orders(customer_id,placed_at)','SELECT id,placed_at,total FROM orders WHERE customer_id=1373 ORDER BY placed_at DESC LIMIT 100'),('store','idx_orders_store_date','CREATE INDEX idx_orders_store_date ON orders(store_id,placed_at)',"SELECT COUNT(*),SUM(total) FROM orders WHERE store_id=7 AND placed_at BETWEEN DATE '2026-01-01' AND DATE '2026-12-31'"),('product','idx_items_product','CREATE INDEX idx_items_product ON order_items(product_id)','SELECT COUNT(*),SUM(quantity*unit_price) FROM order_items WHERE product_id=42')]
   for label,name,index,query in cases:
    c.execute('DROP INDEX IF EXISTS '+name);pg.commit()
    c.execute('EXPLAIN (ANALYZE,BUFFERS) '+query);before='\n'.join(r[0] for r in c.fetchall())
    c.execute(index);c.execute('ANALYZE orders');c.execute('ANALYZE order_items');pg.commit()
    c.execute('EXPLAIN (ANALYZE,BUFFERS) '+query);after='\n'.join(r[0] for r in c.fetchall())
    path=ROOT/'docs'/f'postgres_{label}_plans.txt';path.write_text(f'BEFORE\n{before}\n\nAFTER\n{after}\n')
    print(label,'=>',path.relative_to(ROOT))
if __name__=='__main__':main()
