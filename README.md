# Slate App Testing

This app executes Slate test cases off of a google spreadsheet and updates the sheet with the results.


## Setup
To use the app, set the following environment variables. A `.env` file can be placed the root of the project and will be read a runtime.

| Variable | Notes |
|---|---|
| TEST_PLAN | One of ['commonapp', 'coalition', 'commonapp_transfer', 'peoplesoft'] |
| GSPREAD_CREDENTIAL | The absolute path to a google service account json credential |
| GSPREAD_SHEET_KEY | The key of the spreadsheet containing the test cases |
| GSPREAD_WORKSHEET_NAME | The worksheet name containing the test cases |
| DB_URL | The connection string for your Slate database |


## Usage
Run a test plan by calling run.py with the test plan name (eg, `commonapp`, `commonapp_transfer`, `coalition`, `peoplesoft`). By default, only cases marked as 'Untested', 'Error', or 'Fail' will be executed.

To run test cases, use `run.py`:
```bash
python run.py {test_plan} run
``` 

Use the `--loop` option to have tests executed every 3 minutes:
```bash
python run.py {test_plan} run --loop
```

To reset all test cases for a given test plan:
```bash
python run.py {test_plan} reset
```