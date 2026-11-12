# 📚 Universal Dewey Decimal Classification (DDC) Assistant & Call Number Generator
### Library Processing Section | Technical Services & Cataloging Division

A production-grade web application developed for **Library Processing Sections, Technical Services, Catalogers, and Library Professionals**.

The application serves as an **Expert Dewey Decimal Classification (DDC) Assistant and Call Number Generator**, conforming to the **OCLC DDC 23rd Edition (Volumes 1–4)** and C.K. Sharma's *Practical Handbook of Dewey Decimal Classification*, powered by **Google Gemini 1.5 Pro (temperature: 0.1)** with a high-performance **Hybrid Retrieval-Augmented Generation (RAG)** engine.

---

## 🌟 Key Features

1. **Intelligent DDC 23rd Edition Classification & Call Number Generation:**
   - Ingests subject descriptions, book titles, or academic topics.
   - Identifies the primary discipline, Main Class (000–900), Division (000–990), and Section (000–999).
   - Generates the precise synthesized decimal classification number.
   - Provides a full academic library Call Number (`[DDC] [Cutter Number + Work Mark] [Publication Year]`) and printable physical book spine label.

2. **DDC 23 Volumes 1–4 Hybrid RAG System:**
   - Pre-indexed knowledge base covering all 10 Main Classes, 100 Divisions, and 1,000 Sections.
   - Comprehensive coverage of Auxiliary Tables (Tables 1 through 6) including Standard Subdivisions (-01 to -09), Geographic Areas (Tables 2), Literature Forms (Table 3), Language Subdivisions (Table 4), Ethnic/National Groups (Table 5), and Languages (Table 6).
   - Instant BM25 hybrid search combined with on-demand targeted page extraction from `ddc 23rd.pdf` (4,284 pages).

3. **Google Gemini 1.5 Pro Integration (Precision Engine):**
   - Strictly locked at `temperature: 0.1` for maximum analytical determinism and adherence to official DDC rules.
   - Secure API key configuration (via sidebar or `.env` file).
   - Seamless offline fallback engine if an API key is not yet configured.

4. **Structured Output & Lineage Breakdown:**
   - **Core Subject & Discipline Analysis.**
   - **Hierarchical Lineage Tree:** Main Class -> Division -> Section -> Synthesized Topic.
   - **Number Building & Synthesis Justification:** Clear step-by-step formula and citations of DDC 23 rules and auxiliary tables.
   - **MARC 21 Tag 082** representation for OPAC/Koha integration.

5. **Interactive Tools & Export Options:**
   - **DDC 23 Schedule Browser:** Search and explore the entire 000–999 classification hierarchy.
   - **Auxiliary Tables Explorer:** Search and review Tables 1–6 notations.
   - **Interactive Number Building Sandbox:** Formulate base numbers and attach Table 1/2 facets with live calculation.
   - **One-Click Export:** Download catalog reports as Markdown, JSON, or copy the Call Number directly.

---

## 🔑 How to Get a Free Google Gemini API Key

You can obtain a **100% Free Gemini API key** from Google AI Studio:

1. Go to **[Google AI Studio API Keys](https://aistudio.google.com/app/apikey)**.
2. Sign in with any regular Google account.
3. Click the blue button: **'Create API key'**.
4. Copy your generated API key.
5. In the app:
   - Paste it into the **'Enter your Gemini API Key'** field in the left sidebar and click **'💾 Save Key'** (it will save to `.env` for subsequent runs).
   - Or create a `.env` file in the project folder with:
     ```env
     GEMINI_API_KEY=your_copied_api_key_here
     ```

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your system.
- `ddc 23rd.pdf` placed in the project root directory.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```
The application will launch in your default web browser at `http://localhost:8501`.

---

## 📁 Project Directory Structure

```text
DDC Ai/
├── ddc 23rd.pdf                       # Official 4,284-page DDC 23rd Edition PDF
├── app.py                             # Main Streamlit Web Application
├── requirements.txt                   # Application dependencies
├── .env.example                       # Example environment file
├── core/
│   ├── __init__.py
│   ├── ddc_data.py                    # Complete Summaries (000-999) + Tables 1-6 Knowledge Base
│   ├── rag_engine.py                  # Hybrid BM25 + on-demand PDF retrieval engine
│   ├── gemini_client.py               # Gemini 1.5 Pro API client (temperature=0.1) & offline engine
│   └── cutter_generator.py            # Cutter-Sanborn author number & Call Number builder
├── utils/
│   ├── __init__.py
│   ├── ui_components.py               # Universal styling, badges, spine labels, export formats
│   └── sample_queries.py              # Curated library test queries and canonical problems
└── README.md                          # Documentation and instructions
```

---

## 📚 Operational Context

The application is tailored for the technical processing workflows of:
- **Library Technical Services & Processing Divisions**
- **Cataloging & Classification Departments**
- **Academic, Research, and Public Library Systems**

---

## 📜 Standards Compliance
- **Classification:** OCLC Dewey Decimal Classification, 23rd Edition & C.K. Sharma Practical Handbook.
- **Cataloging Rules:** Anglo-American Cataloguing Rules, 2nd Edition (AACR2) & Resource Description and Access (RDA).
- **Machine-Readable Cataloging:** MARC 21 Bibliographic Format (Field 082: Dewey Decimal Classification Number).
- **Author Marks:** Cutter-Sanborn Three-Figure Author Table.
