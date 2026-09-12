import os
import random
from datetime import datetime, timedelta

import psycopg2
from faker import Faker

fake = Faker()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", 5432),
    "dbname": os.getenv("POSTGRES_DB", "ecommerce_db"),
    "user": os.getenv("POSTGRES_USER", "ecommerce"),
    "password": os.getenv("POSTGRES_PASSWORD", "ecommerce123"),
}

CATEGORIES = ["Electronics", "Clothing", "Books", "Home & Kitchen", "Sports"]
PRODUCTS = [
    ("Wireless Headphones", "Electronics", 79.99),
    ("Running Shoes", "Sports", 59.99),
    ("Python Crash Course", "Books", 29.99),
    ("Coffee Maker", "Home & Kitchen", 49.99),
    ("T-Shirt", "Clothing", 19.99),
    ("Smartphone Stand", "Electronics", 14.99),
    ("Yoga Mat", "Sports", 24.99),
    ("Clean Code Book", "Books", 34.99),
    ("Air Fryer", "Home & Kitchen", 89.99),
    ("Denim Jeans", "Clothing", 44.99),
]


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw_customers (
                customer_id   SERIAL PRIMARY KEY,
                full_name     VARCHAR(100),
                email         VARCHAR(100) UNIQUE,
                city          VARCHAR(100),
                country       VARCHAR(100),
                created_at    TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS raw_products (
                product_id    SERIAL PRIMARY KEY,
                product_name  VARCHAR(100),
                category      VARCHAR(50),
                unit_price    NUMERIC(10, 2),
                created_at    TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS raw_orders (
                order_id      SERIAL PRIMARY KEY,
                customer_id   INT REFERENCES raw_customers(customer_id),
                ordered_at    TIMESTAMP,
                status        VARCHAR(20)
            );

            CREATE TABLE IF NOT EXISTS raw_order_items (
                item_id       SERIAL PRIMARY KEY,
                order_id      INT REFERENCES raw_orders(order_id),
                product_id    INT REFERENCES raw_products(product_id),
                quantity      INT,
                unit_price    NUMERIC(10, 2)
            );
        """)
    conn.commit()


def seed_products(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM raw_products")
        if cur.fetchone()[0] > 0:
            return
        cur.executemany(
            "INSERT INTO raw_products (product_name, category, unit_price) VALUES (%s, %s, %s)",
            PRODUCTS,
        )
    conn.commit()


def generate_daily_data(conn, num_customers=20, num_orders=50):
    with conn.cursor() as cur:
        # Insert customers
        customer_ids = []
        for _ in range(num_customers):
            cur.execute(
                """INSERT INTO raw_customers (full_name, email, city, country)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (email) DO NOTHING
                   RETURNING customer_id""",
                (fake.name(), fake.unique.email(), fake.city(), fake.country()),
            )
            row = cur.fetchone()
            if row:
                customer_ids.append(row[0])

        # Fetch all existing customer ids if no new ones inserted
        if not customer_ids:
            cur.execute("SELECT customer_id FROM raw_customers")
            customer_ids = [r[0] for r in cur.fetchall()]

        # Fetch product ids
        cur.execute("SELECT product_id, unit_price FROM raw_products")
        products = cur.fetchall()

        # Insert orders + order items
        statuses = ["completed", "completed", "completed", "pending", "cancelled"]
        for _ in range(num_orders):
            ordered_at = datetime.now() - timedelta(days=random.randint(0, 90))
            cur.execute(
                "INSERT INTO raw_orders (customer_id, ordered_at, status) VALUES (%s, %s, %s) RETURNING order_id",
                (random.choice(customer_ids), ordered_at, random.choice(statuses)),
            )
            order_id = cur.fetchone()[0]

            for product_id, unit_price in random.sample(products, k=random.randint(1, 3)):
                cur.execute(
                    "INSERT INTO raw_order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                    (order_id, product_id, random.randint(1, 5), unit_price),
                )

    conn.commit()
    print(f"[{datetime.now()}] Inserted {num_orders} orders for {len(customer_ids)} customers.")


if __name__ == "__main__":
    conn = get_connection()
    create_tables(conn)
    seed_products(conn)
    generate_daily_data(conn)
    conn.close()
