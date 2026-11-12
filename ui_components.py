"""
UI Components, Custom Styling, and Export Formatters for DDC Assistant
Designed for Library Processing Sections, Technical Services, and Cataloging Professionals.
"""

import json

# Custom CSS for modern styling, RU green/navy theme, and crisp card layouts
CUSTOM_CSS = """
<style>
/* Main Container & Font Styles */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header Banner Styling */
.ru-header-banner {
    background: linear-gradient(135deg, #0b3d2e 0%, #134e38 50%, #1e3a8a 100%);
    border-radius: 12px;
    padding: 24px 28px;
    color: white;
    box-shadow: 0 4px 20px rgba(11, 61, 46, 0.25);
    margin-bottom: 24px;
    border-left: 6px solid #d4af37;
}

.ru-header-title {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 12px;
}

.ru-header-subtitle {
    font-size: 14px;
    color: #d1fae5;
    margin-top: 6px;
    font-weight: 400;
    line-height: 1.5;
}

/* Call Number Hero Box */
.call-number-hero {
    background: linear-gradient(145deg, #f8fafc, #edf2f7);
    border: 2px solid #0b3d2e;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    margin: 16px 0;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
    position: relative;
}

.call-number-badge {
    background: #0b3d2e;
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 4px 14px;
    border-radius: 20px;
    display: inline-block;
    margin-bottom: 10px;
}

.call-number-display {
    font-family: 'Fira Code', monospace;
    font-size: 38px;
    font-weight: 800;
    color: #0b3d2e;
    letter-spacing: 1px;
    margin: 8px 0;
}

.call-number-full {
    font-family: 'Fira Code', monospace;
    font-size: 20px;
    font-weight: 600;
    color: #1e3a8a;
    background: #e0e7ff;
    padding: 6px 16px;
    border-radius: 8px;
    display: inline-block;
    margin-top: 6px;
}

/* Spine Label Card */
.spine-label-box {
    background: #ffffff;
    border: 2px dashed #94a3b8;
    border-radius: 8px;
    padding: 16px;
    width: 140px;
    margin: 0 auto;
    text-align: center;
    font-family: 'Fira Code', monospace;
    font-weight: 700;
    color: #0f172a;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

/* Hierarchy Step Card */
.hierarchy-card {
    background: #ffffff;
    border-left: 4px solid #10b981;
    border-radius: 8px;
    padding: 12px 18px;
    margin-bottom: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.hierarchy-level {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    color: #047857;
    letter-spacing: 0.5px;
}

.hierarchy-code {
    font-family: 'Fira Code', monospace;
    font-weight: 700;
    background: #ecfdf5;
    color: #065f46;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 14px;
}

.hierarchy-title {
    font-weight: 600;
    color: #1e293b;
    font-size: 14px;
}

/* Justification Box - Clean Second Layout with High Contrast */
.justification-box {
    background-color: #f0fdf4 !important;
    border: 1.5px solid #86efac !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin: 14px 0 !important;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.08) !important;
}

.justification-box,
.justification-box p,
.justification-box span,
.justification-box div,
.justification-box em {
    color: #0f172a !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
}

.justification-box strong {
    color: #14532d !important;
    font-weight: 700 !important;
}

.justification-title {
    font-weight: 800 !important;
    color: #14532d !important;
    font-size: 16px !important;
    margin-bottom: 12px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    border-bottom: 1.5px solid #bbf7d0 !important;
    padding-bottom: 8px !important;
}

.justification-box code {
    background-color: #0f172a !important;
    color: #ffffff !important;
    padding: 3px 8px !important;
    border-radius: 6px !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
}

.justification-box .marc-tag,
.justification-box .marc-tag strong {
    color: #1e3a8a !important;
}

.justification-box .marc-tag code {
    background-color: #1e293b !important;
    color: #93c5fd !important;
}

/* Free Key Alert Box */
.free-key-box {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    padding: 14px 18px;
    border-radius: 8px;
    margin-bottom: 16px;
    font-size: 13px;
    color: #1e40af;
}

/* Tags */
.ru-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 6px;
}
.badge-green { background-color: #dcfce7; color: #15803d; }
.badge-blue { background-color: #dbeafe; color: #1e40af; }
.badge-gold { background-color: #fef3c7; color: #b45309; }
</style>
"""


def render_header():
    """Renders the top branding banner."""
    return """
    <div class="ru-header-banner">
        <h1 class="ru-header-title">
            <span>📚</span> Universal DDC Assistant & Call Number Generator
        </h1>
        <div class="ru-header-subtitle">
            Library Processing Section | Technical Services & Cataloging Division<br/>
            <strong>Dewey Decimal Classification 23rd Edition (Volumes 1–4)</strong> • Powered by Gemini 1.5 Pro (Temp: 0.1) & Hybrid RAG
        </div>
    </div>
    """


def render_call_number_hero(final_ddc: str, full_call_number: str = "", cutter: str = "", year: str = ""):
    """Renders the focal call number result box."""
    full_display = full_call_number if full_call_number else f"{final_ddc} {cutter} {year}".strip()
    return f"""
    <div class="call-number-hero">
        <span class="call-number-badge">Synthesized DDC 23rd Edition Class Number</span>
        <div class="call-number-display">{final_ddc}</div>
        <div>
            <span style="font-size: 13px; color: #64748b; font-weight: 600;">Full Library Call Number (DDC + Cutter + Year):</span><br/>
            <span class="call-number-full">{full_display}</span>
        </div>
    </div>
    """


def render_spine_label(spine_lines: str):
    """Renders an authentic physical library book spine label."""
    formatted_lines = "<br/>".join([line.strip() for line in spine_lines.split("\n") if line.strip()])
    return f"""
    <div style="text-align: center; margin: 10px 0;">
        <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #64748b; font-weight: 700;">Library Spine Label</span>
        <div class="spine-label-box">
            {formatted_lines}
        </div>
    </div>
    """


def render_hierarchy_breakdown(breakdown_list: list):
    """Renders step-by-step lineage cards with distinct visual styling per level."""
    html_cards = []
    level_meta = {
        "Main Class": {"icon": "🌐", "border": "#059669", "badge_bg": "#ecfdf5", "badge_color": "#065f46"},
        "Division": {"icon": "📂", "border": "#0284c7", "badge_bg": "#f0f9ff", "badge_color": "#0369a1"},
        "Section": {"icon": "📑", "border": "#6366f1", "badge_bg": "#eef2ff", "badge_color": "#4338ca"},
        "Standard Subdivision": {"icon": "📊", "border": "#f59e0b", "badge_bg": "#fef3c7", "badge_color": "#b45309"},
        "Synthesized Topic": {"icon": "🎯", "border": "#0b3d2e", "badge_bg": "#dcfce7", "badge_color": "#0b3d2e"},
        "Synthesized Number": {"icon": "🎯", "border": "#0b3d2e", "badge_bg": "#dcfce7", "badge_color": "#0b3d2e"}
    }

    for idx, item in enumerate(breakdown_list):
        lvl = item.get("level", f"Step {idx+1}")
        meta = level_meta.get(lvl, {"icon": "📌", "border": "#10b981", "badge_bg": "#ecfdf5", "badge_color": "#065f46"})
        icon = meta["icon"]
        border_col = meta["border"]
        badge_bg = meta["badge_bg"]
        badge_col = meta["badge_color"]
        code = item.get("code", "")
        title = item.get("title", "")
        
        card = f"""
        <div class="hierarchy-card" style="border-left: 5px solid {border_col}; margin-bottom: 10px; background: #ffffff; padding: 12px 18px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span class="hierarchy-level" style="font-size: 11.5px; font-weight: 800; text-transform: uppercase; color: {border_col}; letter-spacing: 0.5px;">{icon} {lvl}</span>
                <div class="hierarchy-title" style="font-weight: 600; color: #1e293b; font-size: 14px; margin-top: 3px;">{title}</div>
            </div>
            <div>
                <span class="hierarchy-code" style="font-family: 'Fira Code', monospace; font-weight: 800; background: {badge_bg}; color: {badge_col}; padding: 4px 12px; border-radius: 6px; font-size: 14px;">{code}</span>
            </div>
        </div>
        """
        html_cards.append(card)

    return "".join(html_cards)


def generate_markdown_export(result: dict, query: str, author: str, title: str, year: str) -> str:
    """Generates clean, professional markdown report for catalogers."""
    final_ddc = result.get("final_ddc_number", "000")
    full_cn = result.get("full_call_number", final_ddc)
    subject = result.get("core_subject", query)
    discipline = result.get("discipline", "General")
    justification = result.get("number_building_justification", {})
    
    breakdown_md = ""
    for item in result.get("hierarchical_breakdown", []):
        breakdown_md += f"- **{item.get('level')}:** `{item.get('code')}` — {item.get('title')}\n"

    tables_list = justification.get('auxiliary_tables_used', [])
    tables_analysis = justification.get('auxiliary_tables_analysis', '')
    if tables_analysis and "none" not in tables_analysis.lower():
        tables_str = tables_analysis
    elif tables_list and any(t and "none" not in str(t).lower() for t in tables_list):
        tables_str = ", ".join([str(t) for t in tables_list])
    else:
        tables_str = "Auxiliary Tables Checked: None applied (Base schedule notation is sufficiently specific without auxiliary table facet)"

    md = f"""# Dewey Decimal Classification (DDC 23) Cataloging Report
**Library Processing Section | Technical Services & Cataloging Division**

---

### 📋 Material Metadata
- **Title / Subject Query:** {title or query}
- **Author / Filing Element:** {author or 'N/A'}
- **Publication Year:** {year or 'N/A'}
- **Academic Discipline:** {discipline}
- **Core Subject:** {subject}

### 🏷️ Synthesized Call Number
- **DDC 23rd Edition Classification:** `{final_ddc}`
- **Complete Library Call Number:** `{full_cn}`
- **MARC 21 Tag 082:** `{result.get('marc21_082', f'082 04 $a {final_ddc} $2 23')}`

### 🌲 Hierarchical Lineage
{breakdown_md}

### ⚙️ Number Building / Synthesis Justification
- **Base Number:** `{justification.get('base_number', 'N/A')}`
- **Auxiliary Tables Analysis (Tables 1–6):** {tables_str}
- **Formula:** `{justification.get('formula', 'N/A')}`
- **Detailed Explanation:**
  > {justification.get('detailed_explanation', 'N/A')}

### 📝 Cataloger Notes
{result.get('cataloger_notes', 'Classified according to DDC 23rd Edition guidelines for library processing.')}

---
*Generated via Universal DDC Assistant & Call Number Generator*
*Classification Engine: {result.get('source', 'Gemini 1.5 Pro / DDC 23 Hybrid RAG')}*
"""
    return md
