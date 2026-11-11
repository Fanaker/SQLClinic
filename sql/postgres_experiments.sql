-- Run EXPLAIN (ANALYZE, BUFFERS) before AND after each CREATE INDEX.
-- CASE A: Date filter
DROP INDEX IF EXISTS idx_orders_date;
EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*),SUM(total) FROM orders WHERE placed_at >= DATE '2026-08-01' AND placed_at < DATE '2026-09-01';
CREATE INDEX idx_orders_date ON orders(placed_at);
ANALYZE orders;
EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*),SUM(total) FROM orders WHERE placed_at >= DATE '2026-08-01' AND placed_at < DATE '2026-09-01';
-- CASE B: Composite index
DROP INDEX IF EXISTS idx_orders_customer_date;
EXPLAIN (ANALYZE, BUFFERS) SELECT id,placed_at,total FROM orders WHERE customer_id=1373 ORDER BY placed_at DESC LIMIT 100;
CREATE INDEX idx_orders_customer_date ON orders(customer_id,placed_at);
ANALYZE orders;
EXPLAIN (ANALYZE, BUFFERS) SELECT id,placed_at,total FROM orders WHERE customer_id=1373 ORDER BY placed_at DESC LIMIT 100;
-- CASE C: Store selectivity
DROP INDEX IF EXISTS idx_orders_store_date;
EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*),SUM(total) FROM orders WHERE store_id=7 AND placed_at BETWEEN DATE '2026-01-01' AND DATE '2026-12-31';
CREATE INDEX idx_orders_store_date ON orders(store_id,placed_at);
ANALYZE orders;
EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*),SUM(total) FROM orders WHERE store_id=7 AND placed_at BETWEEN DATE '2026-01-01' AND DATE '2026-12-31';
-- CASE D: Line-item search
DROP INDEX IF EXISTS idx_items_product;
EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*),SUM(quantity*unit_price) FROM order_items WHERE product_id=42;
CREATE INDEX idx_items_product ON order_items(product_id);
ANALYZE order_items;
EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*),SUM(quantity*unit_price) FROM order_items WHERE product_id=42;
