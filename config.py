from pathlib import Path
STATUS_COLUMN_NAME = "status"
DELIVERED_STATUS_VALUE = "Delivered"
ORDER_ID_COLUMN_NAME = "order_id"
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"
OUTPUT_FILE_NAME = "summary_report.csv"
ERROR_LOG_NAME = "errors.log"