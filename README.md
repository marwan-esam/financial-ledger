# Financial Ledger API

A robust, ACID-compliant financial backend microservice designed to handle concurrent transactions, stateful data persistence, and secure user authorization. 

## Core Architecture
This project implements enterprise-grade backend patterns to ensure strict data integrity and secure stateless authentication, preventing common vulnerabilities like race conditions and Insecure Direct Object References (IDOR).

### Tech Stack
* **Framework:** FastAPI (Python)
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy 2.0
* **Authentication:** Stateless JSON Web Tokens (PyJWT / OAuth2)
* **Testing:** Pytest / HTTPX

## Key Engineering Features

* **ACID-Compliant Concurrency Locks:** Utilizes PostgreSQL row-level locking (`SELECT ... FOR UPDATE`) during financial transfers to strictly prevent race conditions and double-spending during concurrent API requests.
* **Stateless Authentication:** Implements OAuth2 Password Bearer flow with self-expiring JWTs (HS256 signature) to securely verify user identity without querying a session database.
* **Resource Authorization (IDOR Protection):** Middleware dependency injection automatically verifies both token validity and resource ownership before granting access to sensitive ledger histories.
* **Automated QA Pipeline:** Includes a deterministic `pytest` suite simulating end-to-end user flows to mathematically guarantee security blocks hold under adversarial conditions.

## Local Setup & Testing

**1. Clone and Configure Environment**
```bash
git clone [https://github.com/marwan-esam/financial-ledger.git](https://github.com/marwan-esam/financial-ledger.git)
cd financial-ledger
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Database Initialization**
Ensure PostgreSQL is running locally and a database named `ledger_db` exists, then start the server to automatically build the relational tables:
```bash
uvicorn main:app --reload
```

**3. Run Automated Tests**
```bash
pytest test_main.py
```

## API Documentation
Once the server is running, interactive Swagger UI documentation is automatically generated and available at:
`http://127.0.0.1:8000/docs`
