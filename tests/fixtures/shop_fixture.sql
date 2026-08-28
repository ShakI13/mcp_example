-- Tiny fixture schema for unit tests (not the production shop.db).

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    country TEXT
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    price REAL NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO customers (id, name, email, country) VALUES
    (1, 'Alice', 'alice@example.com', 'Germany'),
    (2, 'Bob', 'bob@example.com', 'USA'),
    (3, 'Carol', 'carol@example.com', 'Germany');

INSERT INTO products (id, name, category, price) VALUES
    (1, 'Widget', 'Gadgets', 10.0),
    (2, 'Gadget', 'Gadgets', 25.0),
    (3, 'Book', 'Media', 15.0);

INSERT INTO orders (id, customer_id, order_date) VALUES
    (1, 1, '2025-01-10'),
    (2, 2, '2025-02-01'),
    (3, 1, '2025-03-15');

INSERT INTO order_items (id, order_id, product_id, quantity) VALUES
    (1, 1, 1, 2),
    (2, 1, 2, 1),
    (3, 2, 3, 4),
    (4, 3, 1, 1);
