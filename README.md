# Slate App Testing

This app executes Slate test cases off of a google spreadsheet and updates the sheet with the results.


## Setup
To use the app, set the following environment variables. A `.env` file can be placed the root of the project and will be read a runtime.

| Variable | Notes |
|---|---|
| DB_URL | The connection string for your Slate database |
| PS_DB_URL | The connection string for your PeopleSoft database (optional) |
| GSPREAD_CREDENTIAL | The absolute path to a google service account json credential |
| GSPREAD_SHEET_KEY | The key of the spreadsheet containing the test cases |
| GSPREAD_WORKSHEET_NAME | The worksheet name containing the test cases |

Optional environment variables that can be set:

| Variable | Notes |
| --- | --- |
| PS_DB_URL | The connection string for your PeopleSoft database. This is required if testing in PeopleSoft. |
| DEBUG | `1` or `0`. This will turn on debug features. |
| COMMONAPP_SHEET_KEY | The sheet key for CommonApp First-Year tests |
| COALITION_SHEET_KEY | The sheet key for Coalition tests |
| COMMONAPP_TRANSFER_SHEET_KEY | The sheet key for CommonApp Transfer tests |
| SLEEP_INTERVAL | The number of seconds between runs when `--loop` flag is set |


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

If your test plan has PeopleSoft Test cases on a worksheet named `PS Test Cases`, you can run the test plan in PeopleSoft mode. Make sure to set the appropriate environment variables.

```bash
python run.py {test_plan} run --mode=peoplesoft
```