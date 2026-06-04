# Financial Ledger API

A robust, ACID-compliant financial backend microservice designed to handle concurrent transactions, stateful data persistence, and secure user authorization. 

## Core Architecture
This project implements enterprise-grade backend patterns to ensure strict data integrity and secure stateless authentication, alongside a fully containerized deployment pipeline.

### Tech Stack
* **Framework:** FastAPI (Python)
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy 2.0
* **Authentication:** Stateless JSON Web Tokens (PyJWT / OAuth2)
* **Infrastructure:** Docker, Docker Compose
* **Testing:** Pytest / HTTPX

## Key Engineering Features

* **Automated Container Orchestration:** Immutable API and database environments managed via Docker Compose. Features isolated internal networking, persistent data volumes, and native PostgreSQL healthchecks to automatically resolve boot sequence race conditions.
* **ACID-Compliant Concurrency Locks:** Utilizes PostgreSQL row-level locking (`SELECT ... FOR UPDATE`) during financial transfers to strictly prevent race conditions and double-spending during concurrent API requests.
* **Defense in Depth (Data Integrity):** Implements database-level strictness utilizing PostgreSQL `CheckConstraints` to prevent logical anomalies (like negative balances) independently of the application layer.
* **Stateless Authentication:** Implements OAuth2 Password Bearer flow with self-expiring JWTs (HS256 signature) to securely verify user identity without querying a session database.
* **Resource Authorization (IDOR Protection):** Middleware dependency injection automatically verifies both token validity and resource ownership before granting access to sensitive ledger histories.
* **Automated QA Pipeline:** Deterministic testing suite built with Pytest and HTTPX, executing within the isolated container bridge to mathematically guarantee security barriers.
* **Database Version Control:** Automated schema migrations utilizing Alembic to track database state changes and programmatically enforce structural requirements during container initialization.

## Local Setup & Deployment

**Prerequisites:** Ensure you have Docker and Docker Compose installed on your system. No local Python virtual environments or bare-metal PostgreSQL installations are required.

**1. Clone the Repository**
```bash
git clone [https://github.com/marwan-esam/financial-ledger.git](https://github.com/marwan-esam/financial-ledger.git)
cd financial-ledger
```

**2. One-Click Boot**
Spin up the completely isolated API and Database architecture in the background:
```bash
docker compose up -d --build
```

**3. API Documentation**
Once the healthchecks pass and the server is live, interactive Swagger UI documentation is automatically generated and available at:
`http://127.0.0.1:8000/docs`

**4. Run Automated Tests**
To execute the deterministic test suite directly inside the isolated container environment:
```bash
docker compose exec api pytest test_main.py
```

**5. Teardown**
To stop the application and cleanly remove the containers and network (your database records will persist safely on the external volume):
```bash
docker compose down
```