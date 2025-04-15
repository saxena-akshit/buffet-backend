# financials_api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import yfinance as yf
import pandas as pd
import numpy as np

from rag_pipeline.interface import answer_question

class RAGView(APIView):
    """
    Example Django REST view that uses the RAG pipeline.
    """
    def get(self, request):
        query = request.GET.get('question', None)
        if not query:
            return Response({"error": "No query provided."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = answer_question(query)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Helper function to safely get data from DataFrame
def safe_get(df, key, year_index=0):
    """
    Safely retrieves data from a pandas DataFrame column based on index key.
    Handles potential KeyErrors if the index doesn't exist.
    Uses the specified year_index (0 for latest, 1 for previous, etc.).
    """
    try:
        # Select the column corresponding to the year index
        # yfinance columns are typically Timestamps, access by position
        if year_index < len(df.columns):
            year_column = df.columns[year_index]
            value = df.loc[key, year_column]
            # Replace NaN with 0 or None for calculations/display
            return 0 if pd.isna(value) else value
        return 'N/A' # Year index out of bounds
    except KeyError:
        return 'N/A' # Key (financial item) not found

# Helper function to format numbers or return N/A
def format_value(value, precision=2, percentage=False):
    """Formats numeric values, returns 'N/A' if input is 'N/A'."""
    if value == 'N/A' or value is None:
        return 'N/A'
    try:
        num = float(value)
        if percentage:
            return f"{num:.{precision}%}"
        else:
            # Add commas for thousands separator, format to precision
            return f"{num:,.{precision}f}"
    except (ValueError, TypeError):
        return 'N/A'

# Helper function to convert DataFrame section to JSON-friendly list of dicts
def statement_to_json(df, years=4):
    """Converts the last 'years' columns of a financial statement DataFrame to JSON."""
    try:
        df_subset = df.iloc[:, :years] # Select latest 'years' columns
        df_subset = df_subset.fillna('N/A') # Replace NaN with 'N/A' string
        # Convert Timestamps to YYYY-MM-DD strings for JSON compatibility
        df_subset.columns = df_subset.columns.strftime('%Y-%m-%d')
        # Reset index to turn financial items into a column
        df_subset = df_subset.reset_index()
        # Rename the index column
        df_subset = df_subset.rename(columns={'index': 'Item'})
        # Convert to list of dictionaries {Item: 'Revenue', '2023-09-30': 1000, ...}
        return df_subset.to_dict(orient='records')
    except Exception:
        # Handle cases where DataFrame might be empty or have fewer columns
        return []


class FinancialDataView(APIView):
    """
    API View to fetch financial statements and calculate Buffett ratios for a stock symbol.
    """
    def get(self, request, stock_symbol):
        """
        Handles GET requests to /api/financials/<stock_symbol>/
        Fetches data from yfinance, calculates ratios, and returns JSON response.
        """
        try:
            stock = yf.Ticker(stock_symbol)

            # Fetch annual data
            # Use .financials for Income Statement, .balance_sheet, .cashflow
            # yfinance might return empty DataFrames if data is unavailable
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow

            # Basic validation: Check if essential dataframes are non-empty
            if income_stmt.empty or balance_sheet.empty:
                 return Response(
                     {"error": f"Could not retrieve sufficient financial data for {stock_symbol}. The symbol might be invalid or data unavailable."},
                     status=status.HTTP_404_NOT_FOUND
                 )

            # --- Calculate Ratios ---
            ratios = []
            num_years = len(income_stmt.columns) # Number of available annual periods

            # Ensure there's at least one year of data
            if num_years < 1:
                 return Response(
                     {"error": f"Insufficient annual data found for {stock_symbol} to calculate ratios."},
                     status=status.HTTP_404_NOT_FOUND
                 )

            # --- Income Statement Ratios ---
            gross_profit = safe_get(income_stmt, 'Gross Profit')
            revenue = safe_get(income_stmt, 'Total Revenue')
            sg_and_a = safe_get(income_stmt, 'Selling General And Administration')
            r_and_d = safe_get(income_stmt, 'Research And Development') # Might not exist
            depreciation = safe_get(income_stmt, 'Reconciled Depreciation') # Might not exist, or named differently
            interest_expense = safe_get(income_stmt, 'Interest Expense')
            operating_income = safe_get(income_stmt, 'Operating Income')
            tax_provision = safe_get(income_stmt, 'Tax Provision')
            pretax_income = safe_get(income_stmt, 'Pretax Income')
            net_income = safe_get(income_stmt, 'Net Income') # Or 'Net Income From Continuing Ops'

            # 1. Gross Margin
            gm_value = (gross_profit / revenue) if all(isinstance(x, (int, float)) for x in [gross_profit, revenue]) and revenue != 0 else 'N/A'
            gm_meets = (gm_value >= 0.40) if isinstance(gm_value, (int, float)) else 'N/A'
            ratios.append({"name": "Gross Margin", "value": format_value(gm_value, percentage=True), "rule": "> 40%", "meets": gm_meets})

            # 2. SG&A Margin
            sga_value = (sg_and_a / gross_profit) if all(isinstance(x, (int, float)) for x in [sg_and_a, gross_profit]) and gross_profit != 0 else 'N/A'
            sga_meets = (sga_value <= 0.30) if isinstance(sga_value, (int, float)) else 'N/A'
            ratios.append({"name": "SG&A / Gross Profit", "value": format_value(sga_value, percentage=True), "rule": "< 30%", "meets": sga_meets})

            # 3. R&D Margin
            rnd_value = (r_and_d / gross_profit) if all(isinstance(x, (int, float)) for x in [r_and_d, gross_profit]) and gross_profit != 0 else 'N/A'
            # Check if R&D exists before evaluating rule
            if r_and_d == 'N/A':
                 rnd_meets = 'N/A (No R&D)'
            elif isinstance(rnd_value, (int, float)):
                 rnd_meets = rnd_value <= 0.30
            else:
                 rnd_meets = 'N/A'
            ratios.append({"name": "R&D / Gross Profit", "value": format_value(rnd_value, percentage=True), "rule": "< 30%", "meets": rnd_meets})

            # 4. Depreciation Margin
            depr_value = (depreciation / gross_profit) if all(isinstance(x, (int, float)) for x in [depreciation, gross_profit]) and gross_profit != 0 else 'N/A'
            if depreciation == 'N/A':
                depr_meets = 'N/A (No Depr.)'
            elif isinstance(depr_value, (int, float)):
                depr_meets = depr_value <= 0.10
            else:
                depr_meets = 'N/A'
            ratios.append({"name": "Depreciation / Gross Profit", "value": format_value(depr_value, percentage=True), "rule": "< 10%", "meets": depr_meets})

            # 5. Interest Expense Margin
            int_value = (interest_expense / operating_income) if all(isinstance(x, (int, float)) for x in [interest_expense, operating_income]) and operating_income != 0 else 'N/A'
            int_meets = (int_value <= 0.15) if isinstance(int_value, (int, float)) else 'N/A'
            ratios.append({"name": "Interest Exp / Operating Income", "value": format_value(int_value, percentage=True), "rule": "< 15%", "meets": int_meets})

            # 6. Income Tax Rate
            tax_value = (tax_provision / pretax_income) if all(isinstance(x, (int, float)) for x in [tax_provision, pretax_income]) and pretax_income != 0 else 'N/A'
            # Rule is subjective ("Current Rate"), so just display value
            ratios.append({"name": "Income Tax Rate", "value": format_value(tax_value, percentage=True), "rule": "Current Corp Rate", "meets": "N/A"}) # No boolean check

            # 7. Net Margin
            nm_value = (net_income / revenue) if all(isinstance(x, (int, float)) for x in [net_income, revenue]) and revenue != 0 else 'N/A'
            nm_meets = (nm_value >= 0.20) if isinstance(nm_value, (int, float)) else 'N/A'
            ratios.append({"name": "Net Margin", "value": format_value(nm_value, percentage=True), "rule": "> 20%", "meets": nm_meets})

            # 8. EPS Growth (Requires at least 2 years of data)
            eps_growth_meets = 'N/A'
            if num_years >= 2:
                eps_latest = safe_get(income_stmt, 'Basic EPS', 0)
                eps_previous = safe_get(income_stmt, 'Basic EPS', 1)
                if all(isinstance(x, (int, float)) for x in [eps_latest, eps_previous]) and eps_previous != 0:
                     # Check if growth is positive (EPS Latest > EPS Previous)
                     eps_growth_meets = "Positive" if eps_latest > eps_previous else "Negative/Flat"
                else:
                     eps_growth_meets = "N/A (Data Missing)"
            else:
                eps_growth_meets = "N/A (<2yrs data)"
            ratios.append({"name": "EPS Growth (YoY)", "value": eps_growth_meets, "rule": "Positive", "meets": (eps_growth_meets == "Positive") if eps_growth_meets.startswith("P") else 'N/A'})


            # --- Balance Sheet Ratios ---
            cash = safe_get(balance_sheet, 'Cash And Cash Equivalents')
            current_debt = safe_get(balance_sheet, 'Current Debt') # Might not exist
            total_liabilities = safe_get(balance_sheet, 'Total Liabilities Net Minority Interest')
            total_equity = safe_get(balance_sheet, 'Total Equity Gross Minority Interest') # Or 'Stockholders Equity'
            preferred_stock = safe_get(balance_sheet, 'Preferred Stock Equity') # Check existence
            retained_earnings_latest = safe_get(balance_sheet, 'Retained Earnings', 0)
            treasury_stock = safe_get(balance_sheet, 'Treasury Stock') # Check existence

            # 9. Cash vs Debt
            cash_debt_meets = 'N/A'
            if current_debt == 'N/A':
                 cash_debt_meets = 'N/A (No Current Debt)'
            elif all(isinstance(x, (int, float)) for x in [cash, current_debt]):
                 cash_debt_meets = "Cash > Debt" if cash > current_debt else "Debt >= Cash"
            ratios.append({"name": "Cash vs Current Debt", "value": cash_debt_meets, "rule": "Cash > Debt", "meets": (cash_debt_meets == "Cash > Debt") if isinstance(cash_debt_meets, str) and cash_debt_meets.startswith("C") else 'N/A'})

            # 11. Debt to Equity (Using Total Liabilities / Total Equity)
            dte_value = (total_liabilities / total_equity) if all(isinstance(x, (int, float)) for x in [total_liabilities, total_equity]) and total_equity != 0 else 'N/A'
            dte_meets = (dte_value < 0.80) if isinstance(dte_value, (int, float)) else 'N/A'
            ratios.append({"name": "Debt to Equity", "value": format_value(dte_value, precision=2), "rule": "< 0.80", "meets": dte_meets})

            # 12. Preferred Stock
            pref_stock_value = format_value(preferred_stock, precision=0) if preferred_stock != 'N/A' else "None Found"
            ratios.append({"name": "Preferred Stock", "value": pref_stock_value, "rule": "None (Buffett Dislikes)", "meets": "N/A"}) # Informational

            # 13. Retained Earnings Growth (Requires at least 2 years)
            re_growth_meets = 'N/A'
            if num_years >= 2:
                retained_earnings_previous = safe_get(balance_sheet, 'Retained Earnings', 1)
                if all(isinstance(x, (int, float)) for x in [retained_earnings_latest, retained_earnings_previous]):
                    re_growth_meets = "Growing" if retained_earnings_latest > retained_earnings_previous else "Not Growing"
                else:
                     re_growth_meets = "N/A (Data Missing)"
            else:
                 re_growth_meets = "N/A (<2yrs data)"
            ratios.append({"name": "Retained Earnings Growth (YoY)", "value": re_growth_meets, "rule": "Consistent Growth", "meets": (re_growth_meets == "Growing") if isinstance(re_growth_meets, str) and re_growth_meets.startswith("G") else 'N/A'})

            # 14. Treasury Stock
            # Check if treasury stock exists and has a non-zero (usually negative) value
            treasury_exists = (treasury_stock != 'N/A' and treasury_stock != 0)
            ratios.append({"name": "Treasury Stock Exists?", "value": "Yes" if treasury_exists else "No", "rule": "Exists (Buybacks)", "meets": treasury_exists})

            # --- Cash Flow Ratios ---
            capex = safe_get(cash_flow, 'Capital Expenditure')
            # Need Net Income again (already fetched)

            # 15. CapEx Margin
            capex_value = abs(capex / net_income) if all(isinstance(x, (int, float)) for x in [capex, net_income]) and net_income != 0 else 'N/A' # Use abs because capex is often negative
            capex_meets = (capex_value < 0.25) if isinstance(capex_value, (int, float)) else 'N/A'
            ratios.append({"name": "CapEx / Net Income", "value": format_value(capex_value, percentage=True), "rule": "< 25%", "meets": capex_meets})


            # --- Prepare Statements for JSON ---
            # Limit to latest 4 years for readability
            income_statement_json = statement_to_json(income_stmt, years=4)
            balance_sheet_json = statement_to_json(balance_sheet, years=4)
            cash_flow_json = statement_to_json(cash_flow, years=4) if not cash_flow.empty else []


            # --- Construct Final Response ---
            response_data = {
                "symbol": stock_symbol.upper(),
                "ratios": ratios,
                "incomeStatement": income_statement_json,
                "balanceSheet": balance_sheet_json,
                "cashFlow": cash_flow_json,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Catch potential errors from yfinance (e.g., network issues, invalid symbol format before Ticker call)
            # Or errors during calculation
            print(f"Error processing {stock_symbol}: {e}") # Log the error server-side
            return Response(
                {"error": f"An error occurred while processing the request for {stock_symbol}. Please check the symbol or try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
