"""Basic usage example for the Antenna Pattern SDK.

Usage:
    pip install -e ".[export]"
    python examples/basic_usage.py <input_csv> <output_pptx>
"""
import logging
import sys
from pathlib import Path

from antenna_sdk import CSVParser, PatternAnalyzer
from antenna_sdk.exporters.pptx import PPTXExporter


def main(csv_path: str, out_path: str) -> None:
    # 1. 設定日誌層級
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    # 2. 解析 CSV
    parser = CSVParser(csv_path)
    parsed_data = parser.parse()

    # 3. 分析數據 (提取矩陣與 2D 切面)
    analyzer = PatternAnalyzer()
    measurement = analyzer.analyze(parsed_data)

    # 4. 匯出為 PPT
    exporter = PPTXExporter(dpi=150)
    exporter.export(measurement, Path(out_path))

    print(f"\n🎉 處理完成！報告已儲存至: {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python basic_usage.py <input.csv> <output.pptx>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
