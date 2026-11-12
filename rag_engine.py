"""
Lightweight DDC Retrieval & Context Builder
Pure Python implementation (no heavy vector or external ranking packages).
Reads from ddc_data knowledge base and extracts targeted text from ddc 23rd.pdf.
"""

import os
import re
import math
from collections import Counter
from typing import List, Dict, Any, Optional
import pypdf

from core.ddc_data import MAIN_CLASSES, DIVISIONS, SECTIONS, TABLES_INFO, DDC_VOLUMES

class DDCRagEngine:
    def __init__(self, pdf_path: str = "ddc 23rd.pdf"):
        self.pdf_path = pdf_path
        self.pdf_available = os.path.exists(pdf_path)
        self.pdf_reader: Optional[pypdf.PdfReader] = None
        self.page_cache: Dict[int, str] = {}
        
        # Build document corpus for lightweight Pure-Python TF-IDF search
        self.corpus_docs: List[Dict[str, Any]] = []
        self.doc_term_freqs: List[Counter] = []
        self.doc_lengths: List[int] = []
        self.idf: Dict[str, float] = {}
        self.avg_doc_len: float = 0.0

        self._build_corpus()
        self._compute_idf()

    def _tokenize(self, text: str) -> List[str]:
        """Fast standard whitespace and alphanumeric tokenizer."""
        cleaned = re.sub(r'[^a-zA-Z0-9\.\-]', ' ', text.lower())
        return [tok for tok in cleaned.split() if len(tok) > 1]

    def _build_corpus(self):
        """Constructs documents from Main Classes, Divisions, Sections, and Tables."""
        # 1. Main Classes
        for code, title in MAIN_CLASSES.items():
            text = f"Main Class {code} {title} Discipline Generalities"
            self.corpus_docs.append({
                "type": "main_class",
                "code": code,
                "title": title,
                "text": text
            })

        # 2. Divisions
        for code, title in DIVISIONS.items():
            main_code = code[0] + "00"
            text = f"Division {code} {title}. Main Class {main_code} {MAIN_CLASSES.get(main_code, '')}"
            self.corpus_docs.append({
                "type": "division",
                "code": code,
                "title": title,
                "main_class": f"{main_code} {MAIN_CLASSES.get(main_code, '')}",
                "text": text
            })

        # 3. Sections
        for code, title in SECTIONS.items():
            div_code = code[:2] + "0"
            main_code = code[0] + "00"
            text = f"Section {code} {title}. Division {div_code} {DIVISIONS.get(div_code, '')}. Main Class {main_code} {MAIN_CLASSES.get(main_code, '')}"
            self.corpus_docs.append({
                "type": "section",
                "code": code,
                "title": title,
                "division": f"{div_code} {DIVISIONS.get(div_code, '')}",
                "main_class": f"{main_code} {MAIN_CLASSES.get(main_code, '')}",
                "text": text
            })

        # 4. Auxiliary Tables
        for table_id, t_info in TABLES_INFO.items():
            t_name = t_info["name"]
            t_desc = t_info["description"]
            for notation, entry_desc in t_info["entries"].items():
                text = f"{t_name} notation {notation}: {entry_desc}. {t_desc}"
                self.corpus_docs.append({
                    "type": "auxiliary_table",
                    "table": table_id,
                    "code": notation,
                    "title": entry_desc,
                    "text": text
                })

        # Compute term frequencies
        for doc in self.corpus_docs:
            tokens = self._tokenize(doc["text"])
            self.doc_term_freqs.append(Counter(tokens))
            self.doc_lengths.append(len(tokens))

        if self.doc_lengths:
            self.avg_doc_len = sum(self.doc_lengths) / len(self.doc_lengths)

    def _compute_idf(self):
        """Computes inverse document frequency for all unique tokens."""
        N = len(self.corpus_docs)
        df_counts = Counter()
        for tf in self.doc_term_freqs:
            for term in tf:
                df_counts[term] += 1

        for term, df in df_counts.items():
            # Standard smoothed BM25/TF-IDF formula
            self.idf[term] = math.log((N - df + 0.5) / (df + 0.5) + 1.0)

    def _get_pdf_reader(self) -> Optional[pypdf.PdfReader]:
        """Lazy load PDF reader."""
        if self.pdf_reader is None and self.pdf_available:
            try:
                self.pdf_reader = pypdf.PdfReader(self.pdf_path)
            except Exception:
                self.pdf_reader = None
        return self.pdf_reader

    def get_pdf_page_text(self, page_number: int) -> str:
        """Extracts and caches page text from ddc 23rd.pdf."""
        if page_number in self.page_cache:
            return self.page_cache[page_number]
        reader = self._get_pdf_reader()
        if reader and 0 <= page_number < len(reader.pages):
            try:
                txt = reader.pages[page_number].extract_text() or ""
                self.page_cache[page_number] = txt
                return txt
            except Exception:
                return ""
        return ""

    def search_ddc(self, query: str, top_k: int = 6) -> List[Dict[str, Any]]:
        """
        Pure-Python BM25/TF-IDF scoring with exact match boost.
        Runs in under 1 millisecond with zero external dependencies.
        """
        tokens = self._tokenize(query)
        if not tokens:
            return []

        q_lower = query.lower()
        k1 = 1.5
        b = 0.75

        scores = []
        for idx, tf in enumerate(self.doc_term_freqs):
            doc_len = self.doc_lengths[idx]
            doc = self.corpus_docs[idx]
            score = 0.0

            for t in tokens:
                if t in tf:
                    freq = tf[t]
                    idf_val = self.idf.get(t, 0.5)
                    numerator = freq * (k1 + 1.0)
                    denominator = freq + k1 * (1.0 - b + b * (doc_len / (self.avg_doc_len or 1.0)))
                    score += idf_val * (numerator / denominator)

            # Boost exact code matches (e.g. user typed '616' or '-5492')
            if doc["code"].lower() in q_lower:
                score += 8.0
            
            # Boost exact title words
            if any(t in doc["title"].lower() for t in tokens):
                score += 2.0

            if score > 0.05:
                scores.append((score, doc))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scores[:top_k]]

    def retrieve_geographic_context(self, query: str) -> Optional[Dict[str, str]]:
        """Detects geographic treatment facets (Bangladesh, South Asia, etc.)."""
        q_lower = query.lower()
        if "rajshahi" in q_lower or "varendra" in q_lower or "pabna" in q_lower or "bogra" in q_lower:
            return {"table": "T2", "code": "-54922", "name": "Rajshahi Division"}
        elif "dhaka" in q_lower:
            return {"table": "T2", "code": "-54923", "name": "Dhaka Division"}
        elif "chittagong" in q_lower or "chattogram" in q_lower:
            return {"table": "T2", "code": "-54924", "name": "Chittagong Division"}
        elif any(w in q_lower for w in ["bangladesh", "bengal", "bangla", "liberation war"]):
            return {"table": "T2", "code": "-5492", "name": "Bangladesh"}
        elif any(w in q_lower for w in ["india", "south asia", "subcontinent"]):
            return {"table": "T2", "code": "-54", "name": "South Asia / India"}
        elif "pakistan" in q_lower:
            return {"table": "T2", "code": "-5491", "name": "Pakistan"}
        elif any(w in q_lower for w in ["united states", "america", "usa"]):
            return {"table": "T2", "code": "-73", "name": "United States"}
        elif any(w in q_lower for w in ["britain", "england", "uk"]):
            return {"table": "T2", "code": "-41", "name": "British Isles"}
        return None

    def retrieve_standard_subdivision(self, query: str) -> Optional[Dict[str, str]]:
        """Detects Table 1 standard subdivision facets (dictionaries, periodicals, research)."""
        q_lower = query.lower()
        if any(w in q_lower for w in ["journal", "periodical", "magazine", "serial"]):
            return {"table": "T1", "code": "-05", "name": "Serial publications"}
        elif any(w in q_lower for w in ["dictionary", "encyclopedia", "glossary"]):
            return {"table": "T1", "code": "-03", "name": "Dictionaries & encyclopedias"}
        elif any(w in q_lower for w in ["research", "methodology", "investigation"]):
            return {"table": "T1", "code": "-072", "name": "Research; statistical methods"}
        elif any(w in q_lower for w in ["handbook", "manual", "guide"]):
            return {"table": "T1", "code": "-02", "name": "Miscellany (Handbooks, manuals)"}
        elif any(w in q_lower for w in ["education", "teaching", "textbook"]):
            return {"table": "T1", "code": "-071", "name": "Education (Study and teaching)"}
        return None

    def assemble_rag_context(self, query: str) -> str:
        """Assembles rich DDC 23rd Edition context for Gemini 1.5 Pro prompt."""
        matches = self.search_ddc(query, top_k=6)
        geo = self.retrieve_geographic_context(query)
        sub = self.retrieve_standard_subdivision(query)

        lines = [
            "=== DDC 23RD EDITION CANONICAL RETRIEVAL CONTEXT ===",
            f"Query: {query}\n",
            "Matched Schedules & Sections:"
        ]

        for m in matches:
            t = m.get("type", "").upper()
            code = m.get("code", "")
            title = m.get("title", "")
            lines.append(f"• [{t}] DDC {code}: {title}")
            if "division" in m:
                lines.append(f"  Lineage: Division {m['division']} -> Main Class {m.get('main_class', '')}")

        if geo or sub:
            lines.append("\nAuxiliary Tables Context (DDC 23 Volume 1):")
            if geo:
                lines.append(f"• [Table 2 Geographic Area] Notation {geo['code']} for '{geo['name']}' (Add directly if instructed, or via Table 1 '-09').")
            if sub:
                lines.append(f"• [Table 1 Standard Subdivision] Notation {sub['code']} for '{sub['name']}' (Drop terminal zero from base division/class unless instructed otherwise).")

        lines.append("\nKey DDC 23 Number Building Principles:")
        lines.append("1. Choose base number from schedules representing main discipline.")
        lines.append("2. Follow schedule addition notes (e.g. 'Add to base number notation from Table 1-6').")
        lines.append("3. Always format with decimal point after the third digit (e.g. 025.431 or 954.92).")
        
        return "\n".join(lines)
