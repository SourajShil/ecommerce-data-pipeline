# End-to-End E-Commerce Data Pipeline

A complete local data platform that generates e-commerce data, loads it into PostgreSQL, transforms it with dbt, orchestrates the workflow with Airflow, and exposes the final marts for Metabase dashboards.

## What This Project Demonstrates

- Python data generation with Faker
- Raw data storage in PostgreSQL 15
- Scheduled orchestration with Apache Airflow 2.8
- Staging, intermediate, and mart transformations with dbt Core 1.7
- Data quality checks with dbt tests
- Business reporting with Metabase
- A reproducible local environment using Docker Compose

## Architecture

```text
Python + Faker
      |
      v
PostgreSQL raw tables
  raw_customers
  raw_products
  raw_orders
  raw_order_items
      |
      v
dbt staging views
  stg_customers, stg_products, stg_orders, stg_order_items
      |
      v
dbt intermediate view
  int_orders_enriched
      |
      v
dbt mart tables
  fct_daily_sales
  fct_product_performance
  fct_customer_rfm
      |
      v
Metabase dashboards
```

## Repository Structure

```text
.
├── dags/ecommerce_pipeline.py       # Airflow DAG
├── data_ingestion/generate_data.py  # Raw table creation and data generation
├── dbt_project/                     # dbt project, models, tests, and profile
├── docker-compose.yml               # PostgreSQL, Airflow, and Metabase services
├── requirements.txt                 # Local Python dependencies
└── README.md
```

## Prerequisites

Install the following before starting:

- Docker Desktop with Docker Compose
- Git
- At least 4 GB of available Docker memory

The repository contains a development `.env` file used by Docker Compose. Its default values are suitable for local learning only. Do not use the default credentials or keys in production.

## A-to-Z Setup and Execution

### 1. Clone the repository

```bash
git clone https://github.com/SourajShil/ecommerce-data-pipeline.git
cd ecommerce-data-pipeline
```

### 2. Review environment settings

The default local connection is:

| Setting | Value |
|---|---|
| PostgreSQL host from your computer | `localhost` |
| PostgreSQL host inside Docker | `postgres` |
| PostgreSQL port | `5432` |
| Database | `ecommerce_db` |
| User | `ecommerce` |
| Password | `ecommerce123` |

Airflow is initialized with the development login `admin / admin`. Change these values before deploying anywhere outside a local environment.

### 3. Build and start the platform

Run this command from the repository root:

```bash
docker compose up --build -d
```

This starts:

| Service | URL | Purpose |
|---|---|---|
| PostgreSQL | `localhost:5432` | Warehouse and raw data store |
| Airflow | http://localhost:8080 | DAG management and logs |
| Metabase | http://localhost:3000 | Dashboard and analysis UI |

Check service status with:

```bash
docker compose ps
```

Wait until PostgreSQL is healthy and Airflow is running before triggering the DAG. The first startup can take several minutes while the Airflow image installs dbt and Faker.

### 4. Trigger the Airflow pipeline

1. Open http://localhost:8080.
2. Sign in with `admin` and `admin`.
3. Find the `ecommerce_pipeline` DAG.
4. Enable it if it is paused.
5. Select **Trigger DAG**.
6. Open the DAG run and monitor the task logs.

The task dependency is:

```text
ingest_raw_data -> dbt_run -> dbt_test
```

The DAG runs daily with `@daily`, starts from January 1, 2024, and has catchup disabled. A manual trigger is the fastest way to create the first dataset.

### 5. Understand the ingestion step

`ingest_raw_data` loads `data_ingestion/generate_data.py` inside the Airflow container. It:

1. Creates the four raw tables if they do not already exist.
2. Seeds the ten products once when `raw_products` is empty.
3. Generates 20 customers and 50 orders per run.
4. Generates one to three line items per order.
5. Assigns order dates across the previous 90 days.
6. Creates `completed`, `pending`, and `cancelled` order statuses.

Each trigger appends generated orders. The generated values are intentionally random, so dashboard totals differ between runs.

### 6. Understand the dbt step

The DAG executes:

```bash
dbt run --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project
dbt test --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project
```

#### Staging views

- `stg_customers`: cleaned customer records
- `stg_products`: product catalog
- `stg_orders`: excludes cancelled orders
- `stg_order_items`: calculates each item `line_total`

#### Intermediate view

- `int_orders_enriched`: joins orders, customers, products, and line items and calculates order revenue

#### Mart tables

| Model | Purpose |
|---|---|
| `fct_daily_sales` | Daily revenue, order count, customer count, and average order value |
| `fct_product_performance` | Product units sold, revenue, and category ranking |
| `fct_customer_rfm` | Recency, frequency, monetary value, and customer segments |

Customer segments include `Champion`, `Loyal`, `At Risk`, and `Lost`. Schema tests cover required, unique, and accepted-value columns.

### 7. Connect Metabase

On the first visit to http://localhost:3000, complete the Metabase setup and add a PostgreSQL database with:

| Field | Value |
|---|---|
| Host | `postgres` |
| Port | `5432` |
| Database name | `ecommerce_db` |
| Username | `ecommerce` |
| Password | `ecommerce123` |

Use the Docker service name `postgres`, not `localhost`, because Metabase connects from inside the Docker network. Start with these questions or dashboard cards:

- Daily revenue trend from `fct_daily_sales`
- Top ten products by revenue from `fct_product_performance`
- Customer segment distribution from `fct_customer_rfm`
- KPI cards for total revenue, total orders, and average order value

> **Metabase note:** The current Compose file configures Metabase to use a PostgreSQL database named `metabase`, but the PostgreSQL initialization only creates `ecommerce_db`. If Metabase cannot start, create the `metabase` database first or update the Metabase database configuration in `docker-compose.yml`.

## Run dbt Locally

With PostgreSQL running and port `5432` available on your computer:

```bash
cd dbt_project
pip install -r ../requirements.txt
dbt debug --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir . --port 8081
```

Open http://localhost:8081 for dbt documentation. The local profile defaults to `localhost`; the Airflow container uses `postgres` as the database host.

## Validation and Troubleshooting

View all service logs:

```bash
docker compose logs -f
```

View a specific service log:

```bash
docker compose logs -f airflow-scheduler
```

Useful checks:

```bash
docker compose ps
docker compose exec postgres pg_isready -U ecommerce
docker compose exec airflow-scheduler dbt debug --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project
```

If Airflow does not open, wait for `airflow-init` to finish and check its logs. If a port is already in use, stop the conflicting process or change the host-side port mapping in `docker-compose.yml`.

## Stop and Clean Up

Stop containers while keeping the PostgreSQL volume:

```bash
docker compose down
```

Stop containers and delete all stored pipeline data:

```bash
docker compose down -v
```

The second command is destructive: it removes the `postgres_data` Docker volume and all raw tables, dbt models, and dashboard source data stored in PostgreSQL.

## License

This project is provided for learning and demonstration purposes.