from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_FILE_NAME = "summary_report.csv"
ERROR_LOG_NAME = "errors.log"
STATUS_COLUMN_NAME = "status"
DELIVERED_STATUS_VALUE = "Delivered"