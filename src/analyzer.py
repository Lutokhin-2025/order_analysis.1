from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd
import logging
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
        self.status_col_name = status_col_name
        self.delivered_status_value = delivered_status_value.lower()
        self.processed_count = 0
        self.error_count = 0

        self.logs_dir.mkdir(exist_ok=True)
        log_path = self.logs_dir / "errors.log"

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(file_handler)
        self.logger = logger

    def load_and_filter(self, filepath: Path) -> Optional[pd.DataFrame]:
        try:
            df = pd.read_csv(filepath, encoding="utf-8")
        except Exception as e:
            self.logger.error(f"Файл '{filepath.name}': ошибка чтения CSV — {e}")
            self.error_count += 1
            return None

        required_cols = [
            "order_id",
            "total_amount",
            self.status_col_name,
        ]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            self.logger.error(
                f"Файл '{filepath.name}': отсутствуют обязательные колонки: {', '.join(missing_cols)}"
            )
            self.error_count += 1
            return None

        coerced_amount = pd.to_numeric(df["total_amount"], errors="coerce")
        if coerced_amount.notnull().sum() < len(df):
            self.logger.error(
                f"Файл '{filepath.name}': обнаружены нечисловые значения в колонке 'total_amount'. Файл пропущен целиком."
            )
            self.error_count += 1
            return None
        df["total_amount"] = coerced_amount

        if not pd.api.types.is_string_dtype(df[self.status_col_name]):
            self.logger.error(f"Файл '{filepath.name}': колонка '{self.status_col_name}' должна быть строковой")
            self.error_count += 1
            return None

        filtered_df = df[
            df[self.status_col_name].str.lower() == self.delivered_status_value
        ].copy()
        return filtered_df

    def calculate_metrics(self, df: pd.DataFrame, *, file_name: str) -> Optional[Dict[str, Any]]:
        if df.empty:
            return None
        total_revenue = df["total_amount"].sum()
        order_count = len(df)
        avg_check = total_revenue / order_count if order_count > 0 else 0.0
        return {
            "file_name": file_name,
            "total_revenue": round(total_revenue, 2),
            "order_count": int(order_count),
            "average_check": round(avg_check, 2),
        }

    def process_one_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        df = self.load_and_filter(filepath)
        if df is None or df.empty:
            return None
        return self.calculate_metrics(df, file_name=filepath.name)

    def process_all_files(self) -> List[Dict[str, Any]]:
        results: List[Dict] = []
        csv_files = sorted(self.data_dir.glob("*.csv"))
        if not csv_files:
            self.logger.error("В папке data/ не найдено ни одного CSV-файла.")
            return results
        for file in csv_files:
            result = self.process_one_file(file)
            if result:
                results.append(result)
                self.processed_count += 1
        return results

    def save_report(self, results: List[Dict]) -> Path:
        output_path = self.report_dir / config.OUTPUT_FILE_NAME
        self.report_dir.mkdir(parents=True, exist_ok=True)
        if results:
            final_df = pd.DataFrame(results).set_index("file_name")
            final_df.to_csv(output_path, encoding="utf-8", float_format='%.2f')
        return output_path