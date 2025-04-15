# Buffett Insights - Backend API

This project provides the Django backend API for the Buffett Insights Financial Analyzer application. It fetches financial statement data and calculates key financial ratios based on Warren Buffett's principles for a given stock symbol.

## Prerequisites

- Python (Recommend 3.9+ or version used in your venv)
- pip (Python package installer)
- Virtualenv (Recommended for managing dependencies)

## Setup Instructions

1.  **Clone the Repository** (if applicable)

    ```bash
    git clone [your-repo-url]
    cd [your-repo-name]/backend
    ```

2.  **Create/Activate Virtual Environment**

    - _Standard Method (if creating inside project):_
      ```bash
      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      ```
    - _Your Method (using external venv):_
      Ensure your existing virtual environment (e.g., located at `../../venv`) is activated. You might need to activate it from its own directory or use its full path.

3.  **Install Dependencies**
    Make sure you have generated a `requirements.txt` file (`pip freeze > requirements.txt` inside the activated venv).

    ```bash
    pip install -r requirements.txt
    # Or using your specific venv path:
    # ../../venv/bin/pip install -r requirements.txt
    ```

4.  **Apply Migrations**

    ```bash
    python manage.py migrate
    # Or using your specific venv path:
    # ../../venv/bin/python manage.py migrate
    ```

5.  **Configure CORS**
    Ensure `django-cors-headers` is installed and configured in `settings.py` (MIDDLEWARE, INSTALLED_APPS, CORS_ALLOWED_ORIGINS) to allow requests from your frontend development server (e.g., `http://localhost:5173`).

6.  **Run the Development Server**
    ```bash
    python manage.py runserver
    # Or using your specific venv path:
    # ../../venv/bin/python manage.py runserver
    ```
    The API will typically be available at `http://127.0.0.1:8000/`.

## API Endpoints

- **`GET /api/financials/<stock_symbol>/`**
  - Retrieves financial statements (Income Statement, Balance Sheet, Cash Flow - last 4 years) and calculated Buffett ratios for the specified `stock_symbol`.
  - Example: `http://127.0.0.1:8000/api/financials/AAPL/`
  - Returns JSON data containing `symbol`, `ratios`, `incomeStatement`, `balanceSheet`, `cashFlow`.

## Technology Stack

- Python
- Django
- Django REST Framework
- yfinance (for fetching financial data)
- Pandas / NumPy (for data manipulation)
- django-cors-headers

---
