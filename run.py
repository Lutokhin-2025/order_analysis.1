from pathlib import Path
import config
from src.analyzer import OrderAnalyzer



def main():
    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    report_dir = project_root / "reports"
    logs_dir = project_root / "logs"

    analyzer = OrderAnalyzer(
        data_dir=data_dir,
        report_dir=report_dir,
        logs_dir=logs_dir,
        status_col_name=config.STATUS_COLUMN_NAME,
        delivered_status_value=config.DELIVERED_STATUS_VALUE,
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