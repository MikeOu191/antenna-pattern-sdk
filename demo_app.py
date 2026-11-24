import streamlit as st
from pathlib import Path
from antenna_sdk import CSVParser, PatternAnalyzer
from antenna_sdk.exporters.pptx import PPTXExporter

st.set_page_config(page_title="Antenna Pattern SDK Demo", layout="wide")
st.title("📡 Antenna Pattern SDK 功能演示")
st.caption("上傳天線量測 CSV，自動解析 → 分析 → 匯出 PPT 報告")

# 1. 檔案上傳區
uploaded_file = st.file_uploader("選擇 CSV 檔案", type="csv")

if uploaded_file is not None:
    # 將上傳的檔案暫存到本地
    temp_path = Path("temp_upload.csv")
    temp_path.write_bytes(uploaded_file.getvalue())

    # 2. 一鍵執行按鈕
    if st.button("🚀 開始分析並匯出 PPT", type="primary"):
        with st.spinner("解析 CSV 中..."):
            parsed = CSVParser(temp_path).parse()
            st.success(f"✅ 編碼: {parsed.encoding} | 區塊: {len(parsed.blocks)} | 頻率: {len(next(iter(parsed.block_frequencies.values()), []))}")

        with st.spinner("計算 2D 切面中..."):
            measurement = PatternAnalyzer().analyze(parsed)
            st.success(f"✅ 提取 {len(measurement.cut_planes)} 個頻率的切面數據")

        with st.spinner("繪圖並匯出 PPT..."):
            output_path = Path("demo_report.pptx")
            PPTXExporter(dpi=150).export(measurement, output_path)
            st.success(f"✅ 報告已生成！")

        # 3. 提供下載按鈕
        st.download_button(
            label="📥 下載 PPT 報告",
            data=output_path.read_bytes(),
            file_name="antenna_report.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )