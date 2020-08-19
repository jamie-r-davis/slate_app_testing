# Slate App Testing

This app executes Slate test cases off of a google spreadsheet and updates the sheet with the results.


## Setup
To use the app, set the following environment variables. A `.env` file can be placed the root of the project and will be read a runtime.

| Variable | Notes |
|---|---|
| GSPREAD_CREDENTIAL | The absolute path to a google service account json credential |
| GSPREAD_SHEET_KEY | The key of the spreadsheet containing the test cases |
| DB_URL | The connection string for your Slate database |


## Usage
By default, only cases marked as 'Untested' or 'Fail' will be executed.

To run test cases, use `run.py`:
```bash
python run.py
``` 

Use the `--loop` option to have tests executed every 3 minutes:
```bash
python run.py --loop
```