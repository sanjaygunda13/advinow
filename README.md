
---

# Project Setup and Usage Guide

Follow these steps to set up and run the project.

**Step 1: Create and activate Virtual Environment**

Activate the virtual environment by running the following command in the project's root directory:

```powershell
python -m venv venv
./venv/Scripts/Activate.ps1
```

**Step 2: Install Dependencies**

Install the required Python packages using pip:

```powershell
pip install -r .\advinow\requirements\requirements.txt
```

**Step 3: Initialize Alembic Migrations**
Navigate to the app directory:

```powershell
cd .\advinow\app\
```

Initialize Alembic migrations:

```powershell
alembic init migrations
```

**Step 4: Update Alembic Configuration**

Open the `env.py` file in the migration folder and find the `target_metadata` variable. Update the line with:

```python
from models import Base
target_metadata = Base.metadata
```

**Step 5: Configure Database Connection**

Open the `alembic.ini` file and find the `sqlalchemy.url` variable. Assign the following value to the variable (without quotes):

```
sqlite:///./test.db
```

**Step 6: Create Database Migration**

Run the following command to create a migration:

```powershell
alembic revision --autogenerate -m "Adding Business, symptoms, and diagnosis tables"
```

**Step 7: Apply Migrations to the Database**

Run the following command to implement migrations on the database:

```powershell
alembic upgrade head
```

**Step 8: Run the Application**

Start the application using Uvicorn:

```powershell
uvicorn run:app --reload
```

**Step 9: Access the API Documentation**

Once the application is running, you can access the API documentation in your web browser. The server should be running on a URL like `http://127.0.0.1:8000` (the port number may vary). To access the API documentation, append "/docs" to the URL, which should look like this:

```
http://127.0.0.1:8000/docs
```

## API Endpoints

**1. Upload CSV File (POST)**

This endpoint allows you to upload a CSV file and save the data in the database.

Parameters:
- CSV file

**2. Get Diagnostic Data**

This endpoint returns data based on user filters. If no filters are applied, it returns the entire result.

Parameters:
- BusinessID (business ID)
- is_diagnosed (drop-down options: True/False)

**3. Delete Data**

This endpoint clears all data in the database.

---
