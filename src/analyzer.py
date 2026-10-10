import config
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd


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
        self.delivered_status_value = delivered_status_value

        # Настройка логирования
        self.logs_dir.mkdir(exist_ok=True)
        log_path = self.logs_dir / "errors.log"
        logging.basicConfig(
            filename=log_path,
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def load_and_filter(self, filepath: Path) -> Optional[pd.DataFrame]:
        """Загружает CSV, проверяет обязательные колонки, фильтрует по статусу."""
        try:
            df = pd.read_csv(filepath, encoding="utf-8")
        except Exception as e:
            self.logger.error(f"Файл '{filepath.name}': ошибка чтения CSV — {e}")
            return None

        required_columns = [
            "order_id",
            "person_id",
            "order_date",
            "status",
            "total_amount",
            "currency",
            "payment_method",
            "shipping_method",
            "notes",
        ]

        missing_cols = [c for c in required_columns if c not in df.columns]
        if missing_cols:
            self.logger.error(
                f"Файл '{filepath.name}': отсутствуют обязательные колонки: {missing_cols}"
            )
            return None

        if self.status_col_name not in df.columns:
            self.logger.error(
                f"Файл '{filepath.name}': отсутствует колонка '{self.status_col_name}'"
            )
            return None

        # Фильтруем по статусу
        filtered_df = df[df[self.status_col_name] == self.delivered_status_value].copy()

        return filtered_df

    def calculate_metrics(self, df: pd.DataFrame, *, file_name: str) -> Optional[Dict[str, Any]]:
        """Считает метрики по доставленным заказам, обрабатывает нечисловые total_amount."""
        if df.empty:
            return None

        # Приводим total_amount к числу, ошибки -> NaN
        df = df.copy()
        df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")

        # Удаляем строки с NaN в total_amount
        clean_df = df.dropna(subset=["total_amount"])

        if clean_df.empty:
            self.logger.error(
                f"Файл '{file_name}': нет валидных значений в колонке total_amount после фильтрации по статусу"
            )
            return None

        total_revenue = clean_df["total_amount"].sum()
        order_count = len(clean_df)
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

    def process_all_files_in_folder(self) -> List[Dict[str, Any]]:
        csv_files = list(self.data_dir.glob("*.csv"))
        results: List[Dict[str, Any]] = []

        for filepath in csv_files:
            result = self.process_one_file(filepath)
            if result is not None:
                results.append(result)

        return results

    def save_report(self, results: List[Dict[str, Any]]) -> Path:
        self.report_dir.mkdir(exist_ok=True)
        df_report = pd.DataFrame(results)
        output_path = self.report_dir / config.OUTPUT_FILE_NAME
        df_report.to_csv(output_path, index=False, encoding="utf-8")
        return output_path