# FISDFunctionCallingDemo

This project demonstrates using Google Cloud Functions to implement a function-calling flow with Gemini, integrating with external APIs (Finhub) and BigQuery. It uses Streamlit for a user interface and leverages the `functions-framework` for local development.

## Project Structure

* **`main.py`**: This is the main entry point for the Cloud Function. It handles user input from the Streamlit interface, interacts with the Gemini model, processes function calls, and displays responses.
* **`helperfinhub.py`**: Contains functions for interacting with the Finhub API.  Each function corresponds to a specific Finhub API endpoint.
* **`helperbqfunction.py`**: Contains functions for interacting with BigQuery.  These functions handle dataset listing, table information retrieval, and SQL query execution.
* **`geminifunctionfinhub.py`**: Defines the function declarations for Finhub API calls that Gemini can use.
* **`geminifunctionsbq.py`**: Defines the function declarations for BigQuery operations that Gemini can use.
* **`helpercode.py`**: Contains utility functions, such as fetching text content from URLs, used to support API interactions.

## Functionality

The application allows users to interact with Gemini via a Streamlit chat interface. User queries can trigger function calls to either Finhub or BigQuery, based on the function declarations provided to the model.  The results from these calls are then incorporated into Gemini's response.  The application handles both serial and parallel function calls from Gemini.

## Local Development

1. **Set up virtual environment:**  Create and activate a virtual environment to manage project dependencies.
2. **Install dependencies:** Install the required packages from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
