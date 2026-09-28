DROP TABLE IF EXISTS payments, order_items, orders, products, customers CASCADE;

CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    signup_date DATE NOT NULL,
    customer_segment VARCHAR(20) NOT NULL CHECK (customer_segment IN ('Retail','Premium','Corporate')),
    city VARCHAR(50) NOT NULL,
    acquisition_channel VARCHAR(50) NOT NULL
);

CREATE TABLE products (
    product_id BIGINT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(80) NOT NULL,
    subcategory VARCHAR(80) NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price > 0)
);

CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    order_status VARCHAR(20) NOT NULL CHECK (order_status IN ('Completed','Cancelled','Returned')),
    payment_method VARCHAR(30) NOT NULL,
    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0)
);

CREATE TABLE order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(order_id),
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price > 0)
);

CREATE TABLE payments (
    payment_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(order_id),
    payment_date DATE NOT NULL,
    payment_amount NUMERIC(12,2) NOT NULL CHECK (payment_amount >= 0),
    payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('Paid','Refunded','Failed'))
);

CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_payments_order ON payments(order_id);
