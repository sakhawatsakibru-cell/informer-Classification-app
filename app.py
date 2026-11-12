"""
Universal Dewey Decimal Classification (DDC) Assistant & Call Number Generator
Designed for Library Processing Sections, Technical Services, and Cataloging Professionals.
Strictly conforms to C.K. Sharma's 'Practical Handbook of Dewey Decimal Classification' & OCLC DDC 23.
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="DDC Assistant - Library Processing Section",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core imports
from core.ddc_data import MAIN_CLASSES, DIVISIONS, SECTIONS, TABLES_INFO, DDC_VOLUMES
from core.cutter_generator import generate_call_number
from core.rag_engine import DDCRagEngine
from core.gemini_client import GeminiDDCClient
from utils.sample_queries import SAMPLE_QUERIES
from utils.ui_components import (
    CUSTOM_CSS,
    render_header,
    render_call_number_hero,
    render_spine_label,
    render_hierarchy_breakdown,
    generate_markdown_export
)

# Inject custom styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = DDCRagEngine(pdf_path="ddc 23rd.pdf")

if "search_id" not in st.session_state:
    st.session_state.search_id = 0

if "classification_result" not in st.session_state:
    st.session_state.classification_result = None

if "last_query" not in st.session_state:
    st.session_state.last_query = ""

if "last_title" not in st.session_state:
    st.session_state.last_title = ""

if "last_subject" not in st.session_state:
    st.session_state.last_subject = ""

if "last_author" not in st.session_state:
    st.session_state.last_author = ""

if "last_year" not in st.session_state:
    st.session_state.last_year = ""

# ==========================================
# SIDEBAR: Configuration & Instructions
# ==========================================
with st.sidebar:
    st.markdown("### 📚 Library Processing Section")
    st.caption("Technical Services & Classification Division\nUniversal DDC 23rd Edition Portal")
    st.divider()

    # Free Gemini API Key section
    st.markdown("### 🔑 Google Gemini API Key")
    env_key = ""
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            env_key = str(st.secrets["GEMINI_API_KEY"])
    except Exception:
        pass
    if not env_key:
        env_key = os.getenv("GEMINI_API_KEY", "")

    api_key_input = st.text_input(
        "Gemini API Key:",
        value=env_key,
        type="password",
        help="Google Gemini API Key from Google AI Studio.",
        placeholder="AIzaSy... or AQ.Ab8..."
    )

    col_key_save, col_key_help = st.columns([1, 1])
    with col_key_save:
        if st.button("💾 Save Key", help="Save key to local .env file"):
            if api_key_input:
                with open(".env", "w") as f:
                    f.write(f"GEMINI_API_KEY={api_key_input.strip()}\n")
                os.environ["GEMINI_API_KEY"] = api_key_input.strip()
                st.success("Key saved to .env!")
            else:
                st.warning("Please enter a key first.")

    with col_key_help:
        st.markdown("[Get Free Key ↗](https://aistudio.google.com/app/apikey)")

    st.divider()

    # Model Configuration
    st.markdown("### ⚙️ Model & Precision Settings")
    selected_model = st.selectbox(
        "AI Engine Model:",
        options=["gemini-1.5-pro", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash"],
        index=0,
        format_func=lambda m: {
            "gemini-1.5-pro": "Gemini 1.5 Pro (Low Temp: 0.1)",
            "gemini-3.5-flash": "Gemini 3.5 Flash (Balanced)",
            "gemini-3.5-flash-lite": "Gemini 3.5 Flash-Lite (Speed)",
            "gemini-3.6-flash": "Gemini 3.6 Flash"
        }.get(m, m),
        help="Gemini 1.5 Pro locked to temperature 0.1 with auto-fallback to prevent hallucinations."
    )
    
    st.markdown("**Temperature:** `0.1` *(Locked for maximum analytical determinism)*")
    st.caption("Adheres strictly to C.K. Sharma manual formulas and DDC 23 schedules.")

    st.divider()

    # Quick Sample Query Selector
    st.markdown("### 🎯 Sample Query Selector")
    selected_sample_idx = st.selectbox(
        "Select a canonical test problem:",
        options=range(len(SAMPLE_QUERIES)),
        format_func=lambda i: f"{SAMPLE_QUERIES[i]['category'].split(':')[-1].strip()}: {SAMPLE_QUERIES[i]['title'][:25]}..."
    )

    if st.button("⚡ Load Selected Query"):
        sample = SAMPLE_QUERIES[selected_sample_idx]
        st.session_state.search_id += 1
        st.session_state[f"title_box_{st.session_state.search_id}"] = sample.get("title", "")
        st.session_state[f"subject_box_{st.session_state.search_id}"] = sample.get("subject", sample.get("description", ""))
        st.session_state[f"author_box_{st.session_state.search_id}"] = sample.get("author", "")
        st.session_state[f"year_box_{st.session_state.search_id}"] = sample.get("year", "")
        st.rerun()

    st.divider()

    # Document & RAG Status
    st.markdown("### 📚 DDC 23 Document Status")
    rag = st.session_state.rag_engine
    if rag.pdf_available:
        st.success("✅ `ddc 23rd.pdf` Loaded\n- 4,284 Pages (Vols 1-4)\n- C.K. Sharma Methods Active")
    else:
        st.info("ℹ️ Using in-memory DDC 23 Knowledge Base.")

# ==========================================
# MAIN APPLICATION BODY
# ==========================================

# Top Banner
st.markdown(render_header(), unsafe_allow_html=True)

# Navigation Tabs
tab_generator, tab_manual, tab_schedules, tab_tables, tab_sandbox = st.tabs([
    "🔍 Call Number Generator & Assistant",
    "📘 C.K. Sharma Classification Methods",
    "📖 DDC 23 Schedule Browser (000–999)",
    "📑 Auxiliary Tables (1–6)",
    "🧮 Number Building Sandbox"
])

# ==========================================
# TAB 1: CALL NUMBER GENERATOR & ASSISTANT
# ==========================================
with tab_generator:
    st.markdown("#### 1. Input Material Information")
    st.caption("All input fields load completely blank by default. Enter fresh bibliographic information for each classification query.")
    
    col_input_title, col_input_subject = st.columns([1, 1])
    with col_input_title:
        title_text = st.text_input(
            "📖 Book Title *:",
            value=st.session_state.get(f"title_box_{st.session_state.search_id}", ""),
            key=f"title_box_{st.session_state.search_id}",
            placeholder="e.g. Teaching of Library Science through correspondence, or Gitanjali"
        )
    with col_input_subject:
        subject_text = st.text_input(
            "🔍 Subject Description / Specific Topic (Optional):",
            value=st.session_state.get(f"subject_box_{st.session_state.search_id}", ""),
            key=f"subject_box_{st.session_state.search_id}",
            placeholder="e.g. Distance education in librarianship, or Bengali poetry modern period"
        )

    col_input_author, col_input_year = st.columns([3, 1])
    with col_input_author:
        author_text = st.text_input(
            "✍️ Author Surname / Name (Optional for Cutter-Sanborn Number):",
            value=st.session_state.get(f"author_box_{st.session_state.search_id}", ""),
            key=f"author_box_{st.session_state.search_id}",
            placeholder="e.g. Sharma, C. K. or Tagore, Rabindranath"
        )
    with col_input_year:
        year_text = st.text_input(
            "📅 Year of Publication (Optional):",
            value=st.session_state.get(f"year_box_{st.session_state.search_id}", ""),
            key=f"year_box_{st.session_state.search_id}",
            placeholder="e.g. 2024"
        )

    col_btn_run, col_btn_clear, col_btn_space = st.columns([2, 1, 3])
    with col_btn_run:
        run_classification = st.button("🚀 Classify & Build Call Number", type="primary", use_container_width=True)
    with col_btn_clear:
        clear_clicked = st.button("🧹 Clear Form", use_container_width=True, help="Reset all fields to blank and clear current results")

    if clear_clicked:
        st.session_state.classification_result = None
        st.session_state.last_title = ""
        st.session_state.last_subject = ""
        st.session_state.last_author = ""
        st.session_state.last_year = ""
        st.session_state.last_query = ""
        st.session_state.search_id += 1
        st.rerun()

    if run_classification:
        clean_title = title_text.strip() if title_text else ""
        clean_subject = subject_text.strip() if subject_text else ""
        clean_author = author_text.strip() if author_text else ""
        clean_year = year_text.strip() if year_text else ""

        if not clean_title and not clean_subject:
            st.error("Please enter a book title or subject description to classify.")
        else:
            if clean_title and clean_subject:
                query_to_classify = f"{clean_title} — {clean_subject}"
            else:
                query_to_classify = clean_title if clean_title else clean_subject

            with st.spinner("Synthesizing Call Number using Gemini 1.5 Pro (Temp: 0.1) & C.K. Sharma DDC Manual..."):
                rag_engine = st.session_state.rag_engine
                # 1. Retrieve RAG context from schedules and tables
                rag_context = rag_engine.assemble_rag_context(query_to_classify)
                
                # 2. Query Gemini / C.K. Sharma Engine
                gemini_client = GeminiDDCClient(
                    api_key=api_key_input.strip() if api_key_input else None,
                    model_name=selected_model
                )
                classification = gemini_client.classify_with_gemini(query_to_classify, rag_context)

                # 3. Generate Complete Call Number (DDC + Cutter-Sanborn + Year)
                final_ddc = classification.get("final_ddc_number", "000")
                call_no_data = generate_call_number(
                    ddc_number=final_ddc,
                    author_name=clean_author,
                    title=clean_title or query_to_classify,
                    publication_year=clean_year
                )

                classification["cutter_mark"] = call_no_data["cutter_mark"]
                classification["full_call_number"] = call_no_data["full_call_number"]
                classification["spine_label"] = call_no_data["spine_label"]
                classification["raw_rag_context"] = rag_context

                # Store metadata for display and export
                st.session_state.classification_result = classification
                st.session_state.last_title = clean_title
                st.session_state.last_subject = clean_subject
                st.session_state.last_author = clean_author
                st.session_state.last_year = clean_year
                st.session_state.last_query = query_to_classify

                # Increment search_id so input fields reset to completely blank on rerun
                st.session_state.search_id += 1
                st.rerun()

    # Display Results if Available
    res = st.session_state.classification_result
    if res:
        st.divider()
        st.markdown("### 🎯 Classification Results & Synthesis Analysis")

        # Top badges
        source_badge_color = "badge-green" if "Gemini" in res.get("source", "") else "badge-gold"
        display_title = st.session_state.last_title or st.session_state.last_query or res.get('core_subject', 'General Material')
        st.markdown(f"""
        <span class="ru-badge badge-blue">Discipline: {res.get('discipline', 'General')}</span>
        <span class="ru-badge badge-green">Subject: {res.get('core_subject', display_title)[:50]}</span>
        <span class="ru-badge {source_badge_color}">Engine: {res.get('source', 'Gemini 1.5 Pro / C.K. Sharma Manual')}</span>
        """, unsafe_allow_html=True)

        # Hero Call Number Box + Spine Label
        col_hero, col_spine = st.columns([3, 1])
        with col_hero:
            st.markdown(
                render_call_number_hero(
                    final_ddc=res.get("final_ddc_number", "000"),
                    full_call_number=res.get("full_call_number", ""),
                    cutter=res.get("cutter_mark", ""),
                    year=st.session_state.last_year
                ),
                unsafe_allow_html=True
            )
        with col_spine:
            st.markdown(render_spine_label(res.get("spine_label", "")), unsafe_allow_html=True)

        # Output Sections: Lineage and Justification
        col_lineage, col_justification = st.columns([1, 1])

        with col_lineage:
            st.markdown("#### 🌲 Step-by-Step Hierarchical Lineage")
            breakdown = res.get("hierarchical_breakdown", [])
            # Support both list of dicts and dict format
            if isinstance(breakdown, dict):
                breakdown_list = [{"level": f"Code {k}", "code": k, "title": v} for k, v in breakdown.items()]
            else:
                breakdown_list = breakdown
            st.markdown(render_hierarchy_breakdown(breakdown_list), unsafe_allow_html=True)

        with col_justification:
            st.markdown("#### ⚙️ Number Building / Synthesis Justification")
            just = res.get("number_building_justification", {})
            if isinstance(just, str):
                method_name = "C.K. Sharma DDC Manual Synthesis"
                base_num = res.get("final_ddc_number", "000")
                table_display = "None applied"
                formula_str = "Base Number + Table / Add Device"
                expl_str = just
            else:
                method_name = just.get("method_used", "C.K. Sharma Number Building Method")
                base_num = just.get("base_number", "N/A")
                
                # Format Auxiliary Tables Used to strictly hold the table number/notation
                tables_used_list = just.get("auxiliary_tables_used", [])
                tables_analysis = just.get("auxiliary_tables_analysis", "")
                
                table_display = ""
                if tables_used_list:
                    clean_list = [str(t).strip() for t in tables_used_list if t and "none" not in str(t).lower()]
                    if clean_list:
                        table_display = ", ".join(clean_list)
                
                if not table_display and tables_analysis and "none" not in tables_analysis.lower():
                    import re
                    match = re.search(r'(Table\s+[1-6][^\.;\n]*)', tables_analysis, re.IGNORECASE)
                    if match:
                        table_display = match.group(1).strip()
                    else:
                        table_display = tables_analysis
                
                if not table_display or "none" in table_display.lower():
                    table_display = "None applied"
                
                formula_str = just.get("formula", "Base + Auxiliary Facet")
                expl_str = just.get("detailed_explanation", "Synthesized according to C.K. Sharma DDC handbook.")

            marc_tag = res.get('marc21_082') or f"082 04 $a {res.get('final_ddc_number', '000')} $2 23"
            st.markdown(f"""
            <div class="justification-box">
                <div class="justification-title">📌 Method: {method_name}</div>
                <p><strong>Base Number:</strong> <code>{base_num}</code></p>
                <p><strong>Auxiliary Tables Used:</strong> <code>{table_display}</code></p>
                <p><strong>Synthesis Formula:</strong> <code>{formula_str}</code></p>
                <p><strong>C.K. Sharma Rule & Explanation:</strong><br/>{expl_str}</p>
                <p class="marc-tag" style="margin-top: 10px; font-size: 13.5px;"><strong>MARC 21 Tag 082:</strong> <code>{marc_tag}</code></p>
            </div>
            """, unsafe_allow_html=True)

        # Cataloger Notes & Context Inspection
        with st.expander("📋 Professional Cataloger Notes & Retrieved DDC Context", expanded=False):
            st.markdown(f"**Cataloger Notes for Technical Processing Staff:**\n{res.get('cataloger_notes', 'N/A')}")
            st.markdown("---")
            st.markdown("**Retrieved RAG Schedules & Tables (DDC 23rd Ed):**")
            st.code(res.get("raw_rag_context", "N/A"), language="markdown")

        # Export & Copy Options
        st.divider()
        st.markdown("#### 📥 Export Generated Results")
        col_copy_md, col_copy_json, col_copy_text = st.columns([1, 1, 1])

        # Markdown export
        display_title = st.session_state.last_title or st.session_state.last_query or res.get("core_subject", "")
        md_export = generate_markdown_export(
            result=res,
            query=st.session_state.last_query or display_title,
            author=st.session_state.last_author,
            title=display_title,
            year=st.session_state.last_year
        )

        with col_copy_md:
            st.download_button(
                label="📄 Download Markdown Report",
                data=md_export,
                file_name=f"ddc_catalog_report_{res.get('final_ddc_number', '000').replace('.', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col_copy_json:
            st.download_button(
                label="📦 Download JSON Record",
                data=json.dumps(res, indent=2),
                file_name=f"ddc_record_{res.get('final_ddc_number', '000').replace('.', '_')}.json",
                mime="application/json",
                use_container_width=True
            )

        with col_copy_text:
            st.code(res.get("full_call_number", ""), language="text")

# ==========================================
# TAB 2: C.K. SHARMA CLASSIFICATION METHODS
# ==========================================
with tab_manual:
    st.markdown("### 📘 C.K. Sharma: Practical Handbook of Dewey Decimal Classification")
    st.caption("Canonical number building rules, formulas, and working methods.")

    col_m1, col_m2 = st.columns([1, 1])

    with col_m1:
        st.markdown("#### 1. The Rule of Zero (Deleting 1 or 2 Zeros)")
        st.info("""
        **Rule 10 (Handbook p. 26):**
        When adding Table 1 Standard Subdivisions (-01 to -09):
        - **If Base ends in '00' (Main Class):** Delete **two zeros** before adding standard subdivision.
          * Example: *Science Museum* = `500` (delete 00) + `074` = **`500.74`**
          * Example: *Encyclopedia of Literature* = `800` (delete 00) + `03` = **`803`**
        - **If Base ends in '0' (Division):** Delete **one zero** before adding standard subdivision.
          * Example: *Journal of Economics* = `330` (delete 0) + `05` = **`330.5`**
          * Example: *Formulas of Chemistry* = `540` (delete 0) + `0212` = **`540.212`**
          * Example: *Teaching of Library Science through correspondence* = `020` (delete 0) + `07154` = **`020.7154`**
        - **If Base does not end in zero:** Add directly with decimal after 3rd digit:
          * Example: *History of Public Libraries in 19th Century* = `027.4` + `09034` = **`027.40934`**
        """)

        st.markdown("#### 2. Table 2: Area Addition Methods")
        st.success("""
        **Handbook p. 27:**
        - **Direct Addition:** When schedule explicitly instructs "Add 'Areas' notation from Table 2":
          * Example: *Wages in Japan* = `331.29` + `-52` (Japan) = **`331.2952`**
          * Example: *Geography of Canada* = `91` + `71` (Canada) = **`917.1`**
          * Example: *Administration of local Govt. in Rajasthan* = `352.0544`
        - **Interposition via Table 1 '-09':** When no direct instruction exists in schedule:
          * Example: *Railroad transportation in Brazil* = `385` + `09` (T1) + `81` (T2 Brazil) = **`385.0981`**
          * Example: *Economic conditions in Bangladesh* = `330` (drop 0) + `09` + `5492` = **`330.95492`**
        """)

    with col_m2:
        st.markdown("#### 3. Schedule Add Device ('Add to Base Number...')")
        st.warning("""
        **Handbook p. 28-29:**
        Enables taking specific facet numbers from another part of schedules:
        - Example: *Cooperative milk production*
          * Base: `334.68` (Cooperatives in manufacturing/extractive)
          * Instruction: *Add numbers following 6 in 620-690*
          * Milk Production = `637.1` (following 6 is `37.1`)
          * **Result = `334.68371`**
        - Example: *Prices of nut fruits*
          * Base: `338.13` + `4.5` (from 634.5 nut fruits) = **`338.1345`**
        - Example: *Soil preparation for rice*
          * Base: `633.18` (Rice) + `1` (Soil preparation from 631.51) = **`633.181`**
        """)

        st.markdown("#### 4. Table 3: Literature & Table 4: Languages")
        st.info("""
        **Literature Formula (Handbook p. 31-35, 47):**
        `[Base Language 810-890] + [Table 3 Form 1-8] + [Period / Collection]`
        - Form: `-1` Poetry, `-2` Drama, `-3` Fiction, `-4` Essays, `-5` Speeches, `-7` Satire
        - Example: *Rabindranath Tagore's poetry: critical appraisal*
          * Base: `891.44` (Bengali literature) + `1` (Poetry) + `5` (Modern period) = **`891.4415`**
        - Example: *Paradise Lost by John Milton (1604-1674)*
          * Base: `82` (English) + `1` (Poetry) + `4` (Period) = **`821.4`**
        - Example: *Bengali Grammar*
          * Base: `491.44` + `5` (Table 4 Grammar) = **`491.445`**
        """)

# ==========================================
# TAB 3: DDC 23 SCHEDULE BROWSER
# ==========================================
with tab_schedules:
    st.markdown("### 📖 DDC 23rd Edition Interactive Schedule Browser")
    st.caption("Explore the 10 Main Classes (First Summary), 100 Divisions (Second Summary), and 1,000 Sections (Third Summary).")

    col_filter_class, col_filter_search = st.columns([1, 2])
    with col_filter_class:
        selected_main_class = st.selectbox(
            "Select Main Class (000 - 900):",
            options=list(MAIN_CLASSES.keys()),
            format_func=lambda k: f"{k} - {MAIN_CLASSES[k]}"
        )
    with col_filter_search:
        schedule_search = st.text_input("Search Schedules by Keyword or Number:", placeholder="e.g. economics, 616, physics, agriculture")

    class_prefix = selected_main_class[0]
    matched_sections = {k: v for k, v in SECTIONS.items() if k.startswith(class_prefix)}

    if schedule_search and schedule_search.strip():
        q_term = schedule_search.strip().lower()
        matched_sections = {
            k: v for k, v in SECTIONS.items() 
            if q_term in k.lower() or q_term in v.lower()
        }

    st.markdown(f"#### Sections in **{selected_main_class} - {MAIN_CLASSES[selected_main_class]}** ({len(matched_sections)} entries)")

    section_data = []
    for code, title in sorted(matched_sections.items()):
        div_code = code[:2] + "0"
        div_name = DIVISIONS.get(div_code, "General")
        section_data.append({
            "DDC Code": code,
            "Section Title": title,
            "Division": f"{div_code} {div_name}"
        })

    st.dataframe(section_data, use_container_width=True, height=450)

# ==========================================
# TAB 4: AUXILIARY TABLES REFERENCE
# ==========================================
with tab_tables:
    st.markdown("### 📑 DDC 23rd Edition Auxiliary Tables (Volume 1)")
    st.caption("Standard Subdivisions, Geographic Areas, Literary Forms, Language Subdivisions, Ethnic Groups, and Languages.")

    table_choice = st.selectbox(
        "Choose an Auxiliary Table:",
        options=list(TABLES_INFO.keys()),
        format_func=lambda k: TABLES_INFO[k]["name"]
    )

    t_info = TABLES_INFO[table_choice]
    st.markdown(f"#### {t_info['name']}")
    st.info(f"**Scope & Purpose:** {t_info['description']}")

    st.markdown("**Key Addition Rules:**")
    for r in t_info["rules"]:
        st.markdown(f"- {r}")

    st.markdown("---")
    st.markdown("##### Notation Entries:")
    
    t_filter = st.text_input("Filter Table Entries (e.g. Bangladesh, dictionary, poetry, -5492):", key="table_filter")
    entries_list = []
    for notation, desc in t_info["entries"].items():
        if not t_filter or t_filter.lower() in notation.lower() or t_filter.lower() in desc.lower():
            entries_list.append({
                "Notation": notation,
                "Description / Topic": desc,
                "Application Example": f"Base + {notation}"
            })

    st.dataframe(entries_list, use_container_width=True, height=400)

# ==========================================
# TAB 5: NUMBER BUILDING SANDBOX
# ==========================================
with tab_sandbox:
    st.markdown("### 🧮 Interactive Number Building Sandbox / Calculator")
    st.caption("Apply the C.K. Sharma Rule of Zero and Area additions live.")

    col_sb_base, col_sb_table = st.columns([1, 1])

    with col_sb_base:
        st.markdown("#### Step 1: Base Schedule Number")
        base_num = st.text_input("Enter Base Number from Schedules:", value="020", help="e.g. 020 Library Science, 540 Chemistry, 500 Science, 331.29 Wages in areas")
        base_desc = st.text_input("Base Subject Description:", value="Library & Information Science")

    with col_sb_table:
        st.markdown("#### Step 2: Select Auxiliary Table Facet")
        facet_type = st.radio(
            "Select Facet Type:",
            options=["Table 1 (Standard Subdivision + Rule of Zero)", "Table 2 (Geographic Area via T1 -09)", "Table 2 (Direct Addition)"],
            index=0
        )

        if "Table 1" in facet_type:
            table_entry = st.selectbox(
                "Table 1 Standard Subdivision:",
                options=list(TABLES_INFO["T1"]["entries"].keys()),
                format_func=lambda k: f"{k}: {TABLES_INFO['T1']['entries'][k]}"
            )
        else:
            table_entry = st.selectbox(
                "Table 2 Geographic Area:",
                options=list(TABLES_INFO["T2"]["entries"].keys()),
                format_func=lambda k: f"{k}: {TABLES_INFO['T2']['entries'][k]}"
            )

    # Synthesis calculation adhering to C.K. Sharma Rule of Zero
    clean_base = base_num.replace(".", "").strip()
    notation_clean = table_entry.replace("-", "").strip()

    if facet_type == "Table 1 (Standard Subdivision + Rule of Zero)":
        # Rule 10: If ends in 00 (main class), delete two zeros. If ends in 0 (division), delete one zero.
        if len(clean_base) == 3 and clean_base.endswith("00"):
            clean_base = clean_base[:-2]
            rule_note = "Deleted TWO zeros (Main Class Rule)"
        elif len(clean_base) == 3 and clean_base.endswith("0"):
            clean_base = clean_base[:-1]
            rule_note = "Deleted ONE zero (Division Rule)"
        else:
            rule_note = "Standard attachment"
        raw_combined = clean_base + notation_clean
        formula_text = f"Base ({base_num}) [{rule_note}] + Table 1 ({table_entry})"
    elif facet_type == "Table 2 (Geographic Area via T1 -09)":
        if len(clean_base) == 3 and clean_base.endswith("00"):
            clean_base = clean_base[:-2]
        elif len(clean_base) == 3 and clean_base.endswith("0"):
            clean_base = clean_base[:-1]
        raw_combined = clean_base + "09" + notation_clean
        formula_text = f"Base ({base_num}) + T1 -09 (Geographical Treatment) + T2 ({table_entry})"
    else:
        raw_combined = clean_base + notation_clean
        formula_text = f"Base ({base_num}) + Direct T2 ({table_entry})"

    if len(raw_combined) > 3:
        synthesized_number = raw_combined[:3] + "." + raw_combined[3:]
    else:
        synthesized_number = raw_combined.ljust(3, "0")

    st.divider()
    st.markdown("#### 🎯 Synthesized Result:")
    col_res_disp, col_res_expl = st.columns([1, 2])
    with col_res_disp:
        st.markdown(f"""
        <div style="background: #0b3d2e; color: white; padding: 20px; border-radius: 12px; text-align: center; font-family: 'Fira Code', monospace; font-size: 32px; font-weight: 800;">
            {synthesized_number}
        </div>
        """, unsafe_allow_html=True)
    with col_res_expl:
        st.markdown(f"**Synthesis Formula:** `{formula_text}`")
        st.markdown(f"**Facet Added:** `{table_entry}`")
        st.markdown(f"**Synthesized Notation Lineage:** `Main Class ({synthesized_number[:1]}00) -> Division ({synthesized_number[:2]}0) -> Base Section ({base_num}) -> Synthesized Result ({synthesized_number})`")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 13px;">
    <strong>Universal DDC Assistant & Call Number Generator</strong><br/>
    Conforming to C.K. Sharma's <em>Practical Handbook of Dewey Decimal Classification</em> & OCLC DDC 23rd Edition.<br/>
    Universal Library Processing & Technical Services Division.
</div>
""", unsafe_allow_html=True)
