# End-to-End E-Commerce Data Pipeline 🛒

A production-style data pipeline that ingests, transforms, and visualizes e-commerce data.

## Stack
| Layer | Tool |
|-------|------|
| Data Generation | Python + Faker |
| Storage | PostgreSQL 15 |
| Orchestration | Apache Airflow 2.8 |
| Transformation | dbt Core 1.7 |
| Dashboard | Metabase |
| Container | Docker Compose |

## Architecture
```
Faker (Python)
     ↓
raw_customers / raw_orders / raw_products / raw_order_items   (PostgreSQL)
     ↓
dbt staging  →  stg_customers, stg_orders, stg_products, stg_order_items
     ↓
dbt intermediate  →  int_orders_enriched
     ↓
dbt marts  →  fct_daily_sales, fct_product_performance, fct_customer_rfm
     ↓
Metabase Dashboards
```

## Quick Start

### 1. Start all services
```bash
docker compose up --build -d
```

### 2. Access services
| Service | URL | Credentials |
|---------|-----|-------------|
| Airflow | http://localhost:8080 | admin / admin |
| Metabase | http://localhost:3000 | setup on first visit |
| Postgres | localhost:5432 | ecommerce / ecommerce123 |

### 3. Trigger the pipeline manually
Go to Airflow → DAGs → `ecommerce_pipeline` → Trigger ▶

### 4. Connect Metabase to Postgres
- Host: `postgres`, Port: `5432`
- Database: `ecommerce_db`, User: `ecommerce`, Password: `ecommerce123`
- Browse schemas: `staging`, `intermediate`, `marts`

## dbt Models

### Staging (views)
- `stg_customers` — cleaned customer records
- `stg_orders` — orders excluding cancelled
- `stg_products` — product catalog
- `stg_order_items` — line items with calculated `line_total`

### Intermediate (views)
- `int_orders_enriched` — orders joined with customers + revenue rollup

### Marts (tables)
| Model | Description |
|-------|-------------|
| `fct_daily_sales` | Revenue, orders, unique customers per day |
| `fct_product_performance` | Units sold + revenue with category rank |
| `fct_customer_rfm` | RFM scoring → Champion / Loyal / At Risk / Lost |

## Run dbt locally
```bash
cd dbt_project
pip install dbt-postgres
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt docs generate && dbt docs serve
```

## Dashboard Suggestions (Metabase)
1. Line chart — `fct_daily_sales.total_revenue` over `sale_date`
2. Bar chart — `fct_product_performance` top 10 by `total_revenue`
3. Pie chart — `fct_customer_rfm.customer_segment` distribution
4. KPI tiles — Total Revenue, Total Orders, Avg Order Value

## Tear Down
```bash
docker compose down -v
```
