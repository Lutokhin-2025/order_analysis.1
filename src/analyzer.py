from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd
import logging
import fnmatch
import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())


class OrderAnalyzer:
    def __init__(
        self,
        data_dir: Path,
        report_dir: Path,
        logs_dir: Path,
        status_col_name: str,
        delivered_status_value: str,
    ):
        self.data_dir = data_dir
        self.report_dir = report_dir
        self.logs_dir = logs_dir
        self.status_col_name = status_col_name.lower()
        self.delivered_status_value = delivered_status_value.lower()
        self.processed_count = 0
        self.error_count = 0


        self.logs_dir.mkdir(exist_ok=True)
        log_path = self.logs_dir / "errors.log"


        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)
        self.logger = logger

    def load_and_filter(self, filepath: Path) -> Optional[pd.DataFrame]:
        try:
            df = pd.read_csv(filepath, encoding="utf-8")
        except Exception as e:
            self._log_error(f"[{filepath.name}] Ошибка чтения CSV — {e}")
            return None

        required_cols = [
            config.ORDER_ID_COLUMN_NAME,
            "total_amount",
            self.status_col_name,
        ]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            self._log_error(
                f"[{filepath.name}] Отсутствуют обязательные колонки: {', '.join(missing_cols)}"
            )
            return None

        coerced_amount = pd.to_numeric(df["total_amount"], errors="coerce")
        if coerced_amount.isnull().any():
            self._log_error(
                f"[{filepath.name}] Обнаружены нечисловые или отсутствующие значения в колонке 'total_amount'."
            )
            return None
        df["total_amount"] = coerced_amount


        if not pd.api.types.is_string_dtype(df[self.status_col_name]):
            self._log_error(
                f"[{filepath.name}] Колонка '{self.status_col_name}' должна быть строковой."
            )
            return None

        return df

    def calculate_metrics(self, filtered_df: pd.DataFrame, *, file_name: str) -> dict[str, float | int]:
        total_revenue = round(filtered_df["total_amount"].sum(), 2)
        order_count = len(filtered_df)
        avg_check = (
            round(total_revenue / order_count, 2)
            if order_count > 0 else 0.0
        )
        return {
            "file_name": file_name,
            "total_revenue": total_revenue,
            "order_count": order_count,
            "average_check": avg_check,
        }

    def process_one_file(self, filepath: Path) -> Dict[str, Any]:
        df = self.load_and_filter(filepath)

        if df is not None and len(df.columns) > 0:
            self.processed_count += 1


        elif df is None or len(df.index) == 0:
            self._log_error(f"[{filepath.name}] Файл не содержит данных.")
            return {
                "file_name": filepath.name,
                "total_revenue": 0.0,
                "order_count": 0,
                "average_check": 0.0,
            }

        filtered_df = df[
            df[self.status_col_name].str.lower() == self.delivered_status_value
        ].copy()


        metrics = {
            "file_name": filepath.name,
            "total_revenue": round(filtered_df["total_amount"].sum(), 2),
            "order_count": len(filtered_df),
            "average_check": (
                round(filtered_df["total_amount"].mean(), 2)
                if len(filtered_df) > 0 else 0.0
            ),
        }
        return metrics

    def _log_error(self, message: str):
        self.logger.error(message)
        self.error_count += 1

    def process_all_files(self) -> list[dict]:
        results: list[dict] = []
        all_files = sorted(self.data_dir.iterdir())
        csv_files = [
            file for file in all_files
            if fnmatch.fnmatch(file.name.lower(), "*.csv")
        ]

        if not csv_files:
            self._log_error("[data] Папка data/ пуста.")
            return results

        for file in csv_files:
            result = self.process_one_file(file)
            results.append(result)


        return results

    def save_report(self, results: List[Dict]) -> Path:
        output_path = self.report_dir / "summary_report.csv"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        final_df = pd.DataFrame(results).set_index("file_name")
        final_df.to_csv(output_path, encoding="utf-8", float_format="%.2f")
        return output_path