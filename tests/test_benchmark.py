from fastapi.testclient import TestClient
from tools.seed import seed,connect
from app.benchmark import CASES,run_case
from app.main import app

def test_seed_database():
 assert seed()==50000
 with connect() as c:assert c.execute('SELECT COUNT(*) FROM order_items').fetchone()[0]>=50000

def test_index_changes_query_plan():
 x=run_case('date_range');assert 'SCAN' in ' '.join(x['before_plan']).upper();assert 'INDEX' in ' '.join(x['after_plan']).upper()

def test_benchmarks_not_fake():
 x=run_case('product');assert x['before_ms']>0 and x['after_ms']>0 and x['engine'].startswith('SQLite')

def test_api():
 with TestClient(app) as client:
  assert client.get('/api/overview').json()['rowcounts']['orders']==50000
  assert client.get('/api/cases').status_code==200
  assert client.post('/api/benchmark/date_range').status_code==200
  assert client.post('/api/benchmark/bad').status_code==404
