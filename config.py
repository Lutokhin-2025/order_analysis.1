from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

OUTPUT_FILE_NAME = "summary_report.csv"
ERROR_LOG_NAME = "errors.log"

STATUS_COLUMN_NAME = "status"
DELIVERED_STATUS_VALUE = "Delivered"