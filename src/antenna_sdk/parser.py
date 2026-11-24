"""CSV loading, keyword localization, and block/frequency extraction (Actions 1–9)."""
from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .exceptions import EncodingDetectionError, CSVFormatError, BlockNotFoundError
from .models import BlockSlice, ParsedCSV, FreqEntry

logger = logging.getLogger(__name__)


class CSVParser:
    """Antenna measurement CSV parser with auto-encoding detection."""

    SUPPORTED_ENCODINGS = ("cp950", "big5", "utf-8-sig", "utf-8", "latin1")
    COL_A_KEYWORDS = ("Theta", "Phi", "Total", "All")
    COL_B_KEYWORDS = ("Total", "Theta", "Phi")

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"檔案不存在: {self.file_path}")
        self._rows: List[List[str]] = []
        self.encoding: Optional[str] = None

    # ---- Action 1 ----
    def _detect_encoding(self) -> str:
        for enc in self.SUPPORTED_ENCODINGS:
            try:
                self.file_path.read_text(encoding=enc)
                self.encoding = enc
                logger.info("偵測到編碼: %s", enc)
                return enc
            except UnicodeDecodeError:
                continue
            except OSError as exc:
                raise CSVFormatError(f"讀取檔案失敗: {exc}") from exc
        raise EncodingDetectionError(f"無法解讀編碼: {self.file_path.name}")

    def _load_rows(self) -> List[List[str]]:
        assert self.encoding is not None
        try:
            with self.file_path.open("r", encoding=self.encoding, newline="") as f:
                self._rows = list(csv.reader(f))
        except Exception as exc:
            raise CSVFormatError(f"CSV 解析失敗: {exc}") from exc
        return self._rows

    # ---- Action 2 ----
    def find_keywords_in_col_a(self) -> Dict[str, List[int]]:
        result: Dict[str, List[int]] = {k: [] for k in self.COL_A_KEYWORDS}
        for idx, row in enumerate(self._rows):
            if row and isinstance(row[0], str):
                low = row[0].strip().lower()
                for kw in self.COL_A_KEYWORDS:
                    if kw.lower() in low:
                        result[kw].append(idx)  # 0-based
        return result

    # ---- Actions 3/4/5 ----
    @staticmethod
    def _slice_between(
        rows: List[List[str]], start_kw: str, end_kw: str,
        kw_pos: Dict[str, List[int]],
    ) -> Optional[BlockSlice]:
        starts = kw_pos.get(start_kw)
        ends = kw_pos.get(end_kw)
        if not starts or not ends:
            return None
        s, e = starts[0], ends[0]
        if s >= e:
            return None
        return BlockSlice(data=rows[s:e], start_row=s)

    def extract_blocks(self, kw_pos: Dict[str, List[int]]) -> Dict[str, BlockSlice]:
        blocks = {
            "eTheta": self._slice_between(self._rows, "Theta", "Phi", kw_pos),
            "ePhi":   self._slice_between(self._rows, "Phi", "Total", kw_pos),
            "Total":  self._slice_between(self._rows, "Total", "All", kw_pos),
        }
        return {k: v for k, v in blocks.items() if v is not None}

    # ---- Action 6 ----
    def scan_col_b_after_all(self, all_row_0based: int) -> Dict[str, List[int]]:
        result: Dict[str, List[int]] = {k: [] for k in self.COL_B_KEYWORDS}
        for idx in range(all_row_0based, len(self._rows)):
            row = self._rows[idx]
            if len(row) > 1 and isinstance(row[1], str):
                low = row[1].strip().lower()
                for kw in self.COL_B_KEYWORDS:
                    if kw.lower() in low:
                        result[kw].append(idx)
        return result

    # ---- Action 7 ----
    def get_all_sub_headers(self, col_b: Dict[str, List[int]]) -> Dict[str, List[str]]:
        headers: Dict[str, List[str]] = {}
        for kw in self.COL_B_KEYWORDS:
            if col_b.get(kw):
                row = self._rows[col_b[kw][0]]
                headers[kw] = [c.strip() for c in row[3:] if str(c).strip()]
            else:
                headers[kw] = []
        return headers

    # ---- Action 8 ----
    def get_all_sub_frequencies(self, col_b: Dict[str, List[int]]) -> Dict[str, List[FreqEntry]]:
        header_rows = {
            kw: (col_b[kw][0] if col_b.get(kw) else None)
            for kw in self.COL_B_KEYWORDS
        }
        if not all(header_rows.values()):
            logger.warning("All 子區塊表頭不完整，跳過頻率提取。")
            return {kw: [] for kw in self.COL_B_KEYWORDS}

        ranges = {
            "Total": (header_rows["Total"], header_rows["Theta"]),
            "Theta": (header_rows["Theta"], header_rows["Phi"]),
            "Phi":   (header_rows["Phi"],   len(self._rows)),
        }
        freqs: Dict[str, List[FreqEntry]] = {}
        for kw, (s, e) in ranges.items():
            lst: List[FreqEntry] = []
            for i in range(s, e):
                row = self._rows[i]
                if len(row) > 2:
                    cell = row[2].strip()
                    try:
                        float(cell)
                        lst.append((i, cell))
                    except ValueError:
                        pass
            freqs[kw] = lst
        self._validate_frequency_consistency(freqs, source="All-sub")
        return freqs

    # ---- Action 9 ----
    def get_block_frequencies(self, blocks: Dict[str, BlockSlice]) -> Dict[str, List[FreqEntry]]:
        freqs: Dict[str, List[FreqEntry]] = {}
        for name, blk in blocks.items():
            lst: List[FreqEntry] = []
            for rel, row in enumerate(blk.data):
                if len(row) > 1:
                    cell = row[1].strip()
                    try:
                        float(cell)
                        lst.append((blk.start_row + rel, cell))
                    except ValueError:
                        pass
            freqs[name] = lst
        self._validate_frequency_consistency(freqs, source="main-blocks")
        return freqs

    @staticmethod
    def _validate_frequency_consistency(
        freqs: Dict[str, List[FreqEntry]], source: str,
    ) -> None:
        counts = [len(v) for v in freqs.values()]
        if len(set(counts)) != 1 or counts[0] == 0:
            logger.warning("[%s] 頻率數量不一致: %s", source, dict(zip(freqs.keys(), counts)))
            return
        keys = list(freqs.keys())
        for i in range(counts[0]):
            ints = [int(float(freqs[k][i][1])) for k in keys]
            if len(set(ints)) != 1:
                logger.warning(
                    "[%s] 第 %d 個頻率整數部分不一致: %s",
                    source, i + 1, {k: freqs[k][i][1] for k in keys},
                )
                return
        logger.info("[%s] 頻率一致性驗證通過 (%d 個)。", source, counts[0])

    # ---- orchestrator ----
    def parse(self) -> ParsedCSV:
        self._detect_encoding()
        self._load_rows()
        col_a = self.find_keywords_in_col_a()
        blocks = self.extract_blocks(col_a)
        if not blocks:
            raise BlockNotFoundError("未在 A 列定位到任何 Theta/Phi/Total 區塊。")

        parsed = ParsedCSV(
            file_path=str(self.file_path),
            encoding=self.encoding or "",
            col_a_keywords=col_a,
            blocks=blocks,
        )
        if col_a.get("All"):
            parsed.col_b_after_all = self.scan_col_b_after_all(col_a["All"][0])
            parsed.all_sub_headers = self.get_all_sub_headers(parsed.col_b_after_all)
            parsed.all_sub_frequencies = self.get_all_sub_frequencies(parsed.col_b_after_all)
        parsed.block_frequencies = self.get_block_frequencies(blocks)

        logger.info(
            "CSV 解析完成: %d 區塊, %d 頻率。",
            len(blocks),
            len(next(iter(parsed.block_frequencies.values()), [])),
        )
        return parsed