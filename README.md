# 🧪 Python BDD API Test Automation

A BDD-based API test automation framework using **pytest-bdd**, **allure-pytest**, and **pyodbc** for Azure SQL Server DB validation.

---

## 📁 Project Structure

```
python bdd project/
├── config/
│   └── db_config.py          # Azure SQL Server credentials
├── features/
│   ├── get_users.feature     # GET API scenarios
│   └── post_users.feature    # POST API scenarios
├── mock_apis/
│   ├── get_api.py            # Mock GET API (Flask, port 5001)
│   └── post_api.py           # Mock POST API (Flask, port 5002)
├── reports/
│   ├── allure-results/       # Raw allure JSON results
│   └── allure-report.html    # Generated HTML report
├── tests/
│   ├── schemas.py            # JSON schemas for response validation
│   ├── db_helper.py          # Azure SQL DB connection & validation
│   ├── test_get_users.py     # GET API step definitions
│   └── test_post_users.py    # POST API step definitions
├── conftest.py               # Session fixtures (mock API lifecycle)
├── pytest.ini                # Pytest config + markers
├── requirements.txt          # All dependencies
├── generate_report.py        # Custom HTML report generator
└── run_tests.bat             # Windows one-click test runner
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure DB (optional)
Edit `config/db_config.py` with your Azure SQL credentials:
```python
DB_CONFIG = {
    "server":   "your-server.database.windows.net",
    "database": "your-database-name",
    "username": "your-azure-username",
    "password": "your-azure-password",
    "driver":   "ODBC Driver 18 for SQL Server",
}
USERS_TABLE = "dbo.Users"
```
> If DB is not configured, DB validation steps are **automatically skipped**.

### 3. Install ODBC Driver (for DB validation)
Download from: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

---

## 🚀 Running Tests

### Full suite
```bash
python -m pytest tests/ -v
```

### Sanity only (happy-path, fast)
```bash
python -m pytest tests/ -v -m sanity
```

### Regression (full suite with edge cases + auth + DB)
```bash
python -m pytest tests/ -v -m regression
```

### Auth tests only
```bash
python -m pytest tests/ -v -m auth
```

### GET API only
```bash
python -m pytest tests/ -v -m get_api
```

### POST API only
```bash
python -m pytest tests/ -v -m post_api
```

---

## 📊 Generating the HTML Report

After running tests:
```bash
python generate_report.py
```
Then open `reports/allure-report.html` in your browser.

---

## 🏷️ Test Markers

| Marker       | Description                                      | When to run         |
|--------------|--------------------------------------------------|---------------------|
| `@sanity`    | Core happy-path tests                            | Every deployment    |
| `@regression`| Full suite — edge cases, auth, DB validation     | Before releases     |
| `@auth`      | Authentication & 401 negative scenarios          | Security checks     |
| `@get_api`   | All GET Users API tests                          | GET API changes     |
| `@post_api`  | All POST Users API tests                         | POST API changes    |

---

## 🔐 Authentication

Both mock APIs use **Bearer token** authentication.

- Valid token: `test-token-123`
- Missing token → `401 Missing authorization header`
- Invalid token → `401 Invalid or expired token`

---

## ✅ Schema Validation

Response bodies are validated against JSON schemas defined in `tests/schemas.py`:

| Schema            | Used for                        |
|-------------------|---------------------------------|
| `USER_SCHEMA`     | Single user (id, name, email)   |
| `USER_LIST_SCHEMA`| Array of users                  |
| `ERROR_SCHEMA`    | Error responses (error field)   |

---

## 🗄️ DB Validation

When DB is configured, tests:
1. Call the API
2. Query the DB for the same record
3. Compare each field (id, name, email) and fail if any mismatch

---

## 📦 Dependencies

| Package          | Version  | Purpose                        |
|------------------|----------|--------------------------------|
| pytest           | 8.2.0    | Test runner                    |
| pytest-bdd       | 7.2.0    | BDD / Gherkin support          |
| allure-pytest    | 2.13.5   | Allure result generation       |
| requests         | 2.31.0   | HTTP client for API calls      |
| flask            | 3.0.3    | Mock API server                |
| jsonschema       | 4.22.0   | JSON schema validation         |
| pyodbc           | 5.1.0    | Azure SQL Server connection     |
