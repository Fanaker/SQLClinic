-- Real PostgreSQL track: schema for order analytics and index benchmarks.
CREATE TABLE IF NOT EXISTS stores(id INT PRIMARY KEY,name TEXT NOT NULL,region TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS customers(id INT PRIMARY KEY,segment TEXT NOT NULL,city TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS products(id INT PRIMARY KEY,name TEXT NOT NULL,category TEXT NOT NULL,price NUMERIC(12,2) NOT NULL);
CREATE TABLE IF NOT EXISTS orders(id BIGINT PRIMARY KEY,customer_id INT NOT NULL REFERENCES customers(id),store_id INT NOT NULL REFERENCES stores(id),placed_at DATE NOT NULL,status TEXT NOT NULL,total NUMERIC(12,2) NOT NULL);
CREATE TABLE IF NOT EXISTS order_items(id BIGINT PRIMARY KEY,order_id BIGINT NOT NULL REFERENCES orders(id),product_id INT NOT NULL REFERENCES products(id),quantity INT NOT NULL,unit_price NUMERIC(12,2) NOT NULL);
