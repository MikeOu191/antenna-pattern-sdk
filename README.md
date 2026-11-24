# Antenna Pattern SDK: From Business Logic to Clean Architecture 📡

This project is not just a parser; it is a **showcase of software engineering evolution**. 
It demonstrates how I translated complex, real-world client requirements (Antenna Measurement CSV Analysis) into a structured, 15-step workflow, and subsequently refactored it from a monolithic script into a robust, layered SDK.

---

## 🚀 1. The Challenge: Business-Driven Development

The client provided raw antenna measurement CSV files and required a comprehensive analysis pipeline. To ensure accuracy and traceability, I broke down the complex requirements into **15 distinct "Actions" (Business Steps)**:

### Phase 1: Data Parsing & Validation (Actions 1–9)
*   **Action 1**: Auto-detect encoding (CP950/Big5/UTF-8) to handle legacy files.
*   **Action 2–5**: Locate keyword blocks (`Theta`, `Phi`, `Total`, `All`) in Column A to isolate data sections.
*   **Action 6–8**: Scan Column B after "All" to extract sub-headers and frequencies, ensuring data integrity.
*   **Action 9**: Cross-validate frequencies across `eTheta`, `ePhi`, and `Total` blocks to prevent data mismatch.

### Phase 2: Core Algorithm & Matrix Extraction (Actions 10–13)
*   **Action 10**: Extract precise 24x13 data matrices for each frequency.
*   **Action 13**: Compute 25-point closed 2D cut-planes (XY, XZ, YZ) for H/V polarizations, applying periodic spline interpolation for smooth physical representation.

### Phase 3: Visualization & Export (Actions 14–15)
*   **Action 15**: Generate high-quality 2D polar plots and export them to a structured PowerPoint report.

---

## 🏗 2. The Refactoring Journey: From Script to SDK

### ❌ Before: The Monolithic Script
Initially, the solution was a single `csv_reader_analyzer.py` file containing ~500 lines of code.
*   **Pain Points**: High coupling (UI, Logic, and I/O mixed), difficult to test, and impossible to extend without breaking existing features.

### ✅ After: Layered Architecture (Clean Architecture)
I refactored the codebase into a **Modular SDK** following the **Separation of Concerns (SoC)** principle:

1.  **Data Layer (`models.py`)**: Defined strict `dataclasses` (`ParsedCSV`, `AntennaMeasurement`) to replace unstructured dictionaries.
2.  **Core Logic Layer (`parser.py`, `analyzer.py`)**: Isolated the 15 Actions into focused classes. The core now depends only on `numpy`.
3.  **Presentation Layer (`exporters/`)**: Implemented the **Open/Closed Principle**. Heavy dependencies (`matplotlib`, `python-pptx`) are lazy-loaded. Adding a new format (e.g., Word) requires zero changes to the core logic.

---

## 📂 3. Project Structure
