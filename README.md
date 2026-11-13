# Qanun Pulse

Qanun Pulse collects the text of Egyptian laws, cleans and normalizes the Arabic text, and computes simple, explainable metrics: how long articles are, how dense the sentences are, which laws change most, and which legal terms appear for the first time. Results are explored in an interactive Streamlit dashboard.

**One codebase, two editions.** The same containers run on a laptop (local edition) and on Azure (cloud edition). Only the settings file changes.

## Architecture

![Architecture](Archeticture.jpg)

| Layer | Purpose | Tables / files |
|---|---|---|
| Raw | Data exactly as collected | `laws`, `articles` |
| Clean | Normalized Arabic text | `articles_normalized` |
| Gold | Metrics ready for the dashboard | `metrics_structure`, `metrics_text`, `metrics_terms`, `dashboard/data/metrics.csv` |

Pipeline (Airflow DAG `qanun_pulse_pipeline`):
`ingest → split_articles → metrics_structure / metrics_text / metrics_terms → export_dashboard_data`

Design choice: the dashboard reads `metrics.csv`, not the database. So it keeps working when the database is stopped to save credit, and it holds no database credentials. The database is used only by the pipeline.

## Data Sources

- **[Manshurat Qanuniya](https://manshurat.org)**: open-access Arabic legal database run by the Law and Society Research Unit at the American University in Cairo.

## Metrics

| # | Metric | What it answers |
|---|---|---|
| 1 | Structure tracker | How many articles and chapters does each version have, and how long is the average article? |
| 2 | Legislative instability index | Which laws are amended most often and by how much text? |
| 3 | Sentence length and density | Is legal language getting denser over time? |
| 4 | New terminology log | Which legal terms appear for the first time in each amendment? |
| 5 | Cross-domain comparison | How does the language of the Constitution compare with the Labor Law and the Penal Code at the same point in time? |

## Requirements

- Docker with Docker Compose v2.20 or newer
- Git
- Python 3.13 and uv (only for running the tests)
- Azure CLI and an Azure subscription (only for the cloud edition)

```bash
git clone https://github.com/Youssefay-cloud/Qanon-Pulse.git
cd Qanon-Pulse
```

## Settings files

Settings live in env files in the repo root. The real ones contain passwords and are **not** committed (see `.gitignore`).

| File | Purpose | In Git |
|---|---|---|
| `.env.example` | Template with placeholders | Yes |
| `.env.local` | Local edition | No |
| `.env.cloud` | Cloud edition | No |

`.env.example`:

```
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/qanon_db
POSTGRES_USER=xxx
POSTGRES_PASSWORD=xxx
COMPOSE_PROFILES=local
```

Create your own copies and fill in the values:

```bash
cp .env.example .env.local
cp .env.example .env.cloud
```

`COMPOSE_PROFILES=local` starts the local `db` and `pgadmin` containers. In `.env.cloud` it is left empty, so no local database starts.

## Run local

1. In `.env.local`, set a local user and password, and make `DATABASE_URL` point to the `db` container:

   ```
   DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@db:5432/qanon_db
   POSTGRES_USER=USER
   POSTGRES_PASSWORD=PASSWORD
   COMPOSE_PROFILES=local
   ```

2. Start the stack:

   ```bash
   docker compose --env-file .env.local up -d --build
   ```

3. Open Airflow at <http://localhost:8081> and trigger `qanun_pulse_pipeline`. Wait until every task is green.
4. Open the dashboard at <http://localhost:8501>. pgAdmin is at <http://localhost:5050>.

Run the Arabic text tests:

```bash
cd transform
uv run pytest
```

## Run on Azure

Everything below is done with the Azure CLI, so it can be repeated exactly. Replace the names in capitals or in `$VARIABLES` with your own.

**Allowed regions.** Student subscriptions allow only a few regions. List them with:

```bash
az policy assignment list --query "[].parameters.listOfAllowedLocations.value" -o json
```

This project used `germanywestcentral` (registry and Container Apps) and `denmarkeast` (database, because `Standard_B1ms` was not available elsewhere). The resource group's own region does not matter.

### 1. Account, budget, resource group

```bash
winget install -e --id Microsoft.AzureCLI
az login
az account show --query "{name:name, state:state}"
```

Budget: in the portal, Cost Management → Budgets, create a $20 monthly budget with an alert at 80%.

Register the services (once per subscription):

```bash
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.DBforPostgreSQL
az provider show --namespace Microsoft.App --query registrationState
```

Create the resource group (one folder for everything, deletable with one command):

```bash
az group create --name qanun-pulse-rg --location westeurope
az group show --name qanun-pulse-rg --query "{name:name, location:location}"
```

### 2. Container registry and dashboard image

```bash
az acr create --resource-group qanun-pulse-rg --name qanunpulseyoussef --sku Basic --location germanywestcentral
az acr login --name qanunpulseyoussef

docker build -f dashboard/Dockerfile -t qanunpulse-dashboard:latest .
docker tag qanunpulse-dashboard:latest qanunpulseyoussef.azurecr.io/dashboard:v1
docker push qanunpulseyoussef.azurecr.io/dashboard:v1
az acr repository show-tags --name qanunpulseyoussef --repository dashboard -o table
```

The image contains `dashboard/data/metrics.csv`, copied in by `COPY dashboard/ ./dashboard/`. Run the pipeline once first so the file exists.

### 3. Dashboard on Container Apps

```bash
az extension add --name containerapp --upgrade
az containerapp env create --name qanun-env --resource-group qanun-pulse-rg --location germanywestcentral
az acr update --name qanunpulseyoussef --admin-enabled true

az containerapp create --name qanun-dashboard --resource-group qanun-pulse-rg \
  --environment qanun-env \
  --image qanunpulseyoussef.azurecr.io/dashboard:v1 \
  --registry-server qanunpulseyoussef.azurecr.io \
  --registry-username qanunpulseyoussef \
  --registry-password $(az acr credential show --name qanunpulseyoussef --query "passwords[0].value" -o tsv) \
  --target-port 8501 --ingress external \
  --cpu 0.25 --memory 0.5Gi --min-replicas 0 --max-replicas 1

az containerapp show --name qanun-dashboard --resource-group qanun-pulse-rg \
  --query properties.configuration.ingress.fqdn -o tsv
```

`--min-replicas 0` scales the app to zero when nobody visits, so it costs almost nothing. The first visit after idle takes a few seconds.

Live demo: <https://qanun-dashboard.niceglacier-8c7e814e.germanywestcentral.azurecontainerapps.io> (may be removed after grading).

### 4. Cloud database

Choose a password (12+ characters, letters and digits only) and type it without echo:

```bash
read -s -p "DB password: " PGPASS; echo

az postgres flexible-server create --resource-group qanun-pulse-rg --name qanun-pg2 \
  --location denmarkeast --admin-user qanunadmin --admin-password "$PGPASS" \
  --tier Burstable --sku-name Standard_B1ms --storage-size 32 --version 16 \
  --public-access $(curl -s https://api.ipify.org)

az postgres flexible-server db create --resource-group qanun-pulse-rg --server-name qanun-pg2 --name qanon_db

az postgres flexible-server show --resource-group qanun-pulse-rg --name qanun-pg2 \
  --query "{name:name, state:state, host:fullyQualifiedDomainName, location:location}"

az postgres flexible-server firewall-rule list --resource-group qanun-pulse-rg --server-name qanun-pg2 -o table
```

If your IP changes, add it again:

```bash
az postgres flexible-server firewall-rule create --resource-group qanun-pulse-rg --name qanun-pg2 \
  --rule-name my-ip --start-ip-address NEW_IP --end-ip-address NEW_IP
```

Test the connection (Azure requires SSL):

```bash
docker run --rm -it postgres:18 psql "host=qanun-pg2.postgres.database.azure.com port=5432 dbname=qanon_db user=qanunadmin sslmode=require"
```

### 5. Run the pipeline against Azure

In `.env.cloud`, use the same password, with no quotes and no spaces:

```
DATABASE_URL=postgresql+psycopg2://qanunadmin:PASSWORD@qanun-pg2.postgres.database.azure.com:5432/qanon_db?sslmode=require
COMPOSE_PROFILES=
```

Start Airflow with the cloud settings (no local `db` starts):

```bash
docker compose --env-file .env.cloud up -d --force-recreate airflow
```

Open <http://localhost:8081>, trigger `qanun_pulse_pipeline`, and wait until every task is green. Then check the data in Azure:

```bash
docker run --rm -it postgres:18 psql "host=qanun-pg2.postgres.database.azure.com port=5432 dbname=qanon_db user=qanunadmin sslmode=require" -c "\dt"
```

Same code, same containers: only `DATABASE_URL` changed.

### 6. Refresh the cloud dashboard when the data changes

The pipeline writes to the database immediately, but the cloud dashboard shows the `metrics.csv` baked into its image. To update it:

1. Run the DAG. It writes a new `dashboard/data/metrics.csv`.
2. Build, tag, and push a new version, then update the app:

```bash
docker build -f dashboard/Dockerfile -t qanunpulse-dashboard:latest .
docker tag qanunpulse-dashboard:latest qanunpulseyoussef.azurecr.io/dashboard:v3
docker push qanunpulseyoussef.azurecr.io/dashboard:v3
az containerapp update --name qanun-dashboard --resource-group qanun-pulse-rg --image qanunpulseyoussef.azurecr.io/dashboard:v3
```

Use a new version number each time (`v4`, `v5`, ...).

### 7. Cost control and cleanup

The database is the main cost. Stop it when idle (Azure restarts it automatically after 7 days):

```bash
az postgres flexible-server stop --resource-group qanun-pulse-rg --name qanun-pg2
az postgres flexible-server start --resource-group qanun-pulse-rg --name qanun-pg2
```

Delete everything when the project is finished:

```bash
az group delete --name qanun-pulse-rg --yes --no-wait
```

## Project Status

| Stage | Status |
|---|---|
| Ingestion (JSON to PostgreSQL) | Done |
| Arabic normalization (`articles_normalized`) | Done |
| Article splitter | Done |
| Metrics computation | Done |
| Airflow orchestration | Done |
| Dashboard (Streamlit) | Done |
| Cloud deployment (Azure: dashboard and database) | Done |