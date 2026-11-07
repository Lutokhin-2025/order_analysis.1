from pathlib import Path
import sys
import config
from src.analyzer import OrderAnalyzer

def main():
    PROJECT_ROOT = Path(sys.argv[0]).parent.resolve()
    analyzer = OrderAnalyzer(
        data_dir=PROJECT_ROOT / "data",
        report_dir=PROJECT_ROOT / "reports",
        logs_dir=PROJECT_ROOT / "logs",
        status_col_name=config.STATUS_COLUMN_NAME,
        delivered_status_value=config.DELIVERED_STATUS_VALUE,
        output_filename=config.OUTPUT_FILE_NAME,
    )
    results = analyzer.process_all_files()
    print(f"Обработано файлов: {analyzer.processed_count}")
    print(f"Файлов с ошибками: {analyzer.error_count}")
    if results:
        output_path = analyzer.save_report(results)
        print(f"Сохранён отчёт в: {output_path}")
    else:
        print("Не удалось обработать ни один файл. Проверьте logs/errors.log")


if __name__ == "__main__":
    main()