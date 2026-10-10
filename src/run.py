import config
from src.analyzer import OrderAnalyzer

def main():
    analyzer = OrderAnalyzer(
        data_dir=config.DATA_DIR,
        report_dir=config.REPORTS_DIR,
        logs_dir=config.LOGS_DIR,
        status_col_name=config.STATUS_COLUMN_NAME,
        delivered_status_value=config.DELIVERED_STATUS_VALUE,
    )

    results = analyzer.process_all_files_in_folder()

    all_csv_files = list(config.DATA_DIR.glob("*.csv"))
    error_count = len(all_csv_files) - len(results)

    print(f"Обработано файлов: {len(results)}")
    print(f"Файлов с ошибками: {error_count}")

    if results:
        output_path = analyzer.save_report(results)
        print(f"Сохранён отчёт в: {output_path}")
    else:
        print("Не удалось обработать ни один файл. Проверьте logs/errors.log")

if __name__ == "__main__":
    main()