import streamlit as st
import os
import pandas as pd
from detector import detect_bugs
from ga_engine import evolve_fix
from validator import validate_fix
from memory import save_fix, recall_similar_fix
from report import generate_report

# =====================================================================
# Page Configuration
# =====================================================================
st.set_page_config(
    page_title="Code Review Agent",
    page_icon="🤖",
    layout="wide"
)

# =====================================================================
# Initialize Session State
# =====================================================================
if "bugs" not in st.session_state:
    st.session_state["bugs"] = []
if "code" not in st.session_state:
    st.session_state["code"] = ""
if "fixes" not in st.session_state:
    st.session_state["fixes"] = {}
if "generations" not in st.session_state:
    st.session_state["generations"] = 3
if "population_size" not in st.session_state:
    st.session_state["population_size"] = 4

# =====================================================================
# Sidebar Section
# =====================================================================
st.sidebar.header("Settings")
st.sidebar.text_input("Groq API Key", type="password", key="api_key")

if st.session_state.get("api_key"):
    st.sidebar.success("✅ API Key Set")

st.sidebar.slider("Generations", min_value=3, max_value=5, key="generations")
st.sidebar.slider("Population Size", min_value=4, max_value=6, key="population_size")

# =====================================================================
# Header Section
# =====================================================================
st.title("🤖 Autonomous Code Review & Bug Fix Agent")
st.caption("Powered by Groq AI + Genetic Algorithms")

# Hardcoded Bug Samples
BUG_1_CODE = """def divide_numbers(a, b):
    # Bug: division by zero if b is 0
    result = a / b
    return result
"""

BUG_2_CODE = """def read_log_file(filename):
    # Bug: file not closed properly
    f = open(filename, 'r')
    data = f.read()
    return data
"""

BUG_3_CODE = """def calculate_factorial(n):
    # Bug: infinite recursion if n is negative
    if n == 0:
        return 1
    return n * calculate_factorial(n - 1)
"""

# =====================================================================
# Tabs Layout
# =====================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Code Input",
    "🐛 Bug Detection", 
    "🧬 Fix Evolution (GA)",
    "📄 Results & Report"
])

# =====================================================================
# Tab 1: Code Input
# =====================================================================
with tab1:
    st.write("### Load Sample Buggy Code")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Bug 1: Division by Zero"):
            st.session_state["input_code"] = BUG_1_CODE
    with col2:
        if st.button("Bug 2: File Not Closed"):
            st.session_state["input_code"] = BUG_2_CODE
    with col3:
        if st.button("Bug 3: Infinite Recursion"):
            st.session_state["input_code"] = BUG_3_CODE
            
    if "input_code" not in st.session_state:
        st.session_state["input_code"] = ""
        
    code_input = st.text_area("Paste Python Code to Analyze", height=300, key="input_code")
    
    if st.button("🔍 Start Analysis"):
        api_key = st.session_state.get("api_key", "").strip()
        if not api_key:
            st.warning("Please enter your Groq API Key in the sidebar.")
        elif not code_input.strip():
            st.warning("Please enter some Python code to analyze.")
        else:
            with st.spinner("Analyzing code for bugs..."):
                try:
                    found_bugs = detect_bugs(code_input, api_key)
                    if not found_bugs:
                        st.error(
                            "No bugs detected — this may mean the code is clean, "
                            "OR the API call failed. Check your terminal console "
                            "for [DEBUG] error messages."
                        )
                    else:
                        st.session_state["bugs"] = found_bugs
                        st.session_state["code"] = code_input
                        st.session_state["fixes"] = {}
                        st.success(f"Analysis completed! Found {len(found_bugs)} bug(s).")
                except Exception as e:
                    st.error(f"Error during bug detection: {e}")

# =====================================================================
# Tab 2: Bug Detection
# =====================================================================
with tab2:
    if not st.session_state["bugs"]:
        st.info("No bugs detected yet. Run analysis in 'Code Input' tab.")
    else:
        st.write("### Bug Detection Summary")
        st.metric(label="Total Bugs Found", value=len(st.session_state["bugs"]))
        
        # Severity Chart
        severities = [str(bug.get("severity", "low")).lower() for bug in st.session_state["bugs"]]
        counts = {"high": severities.count("high"), "medium": severities.count("medium"), "low": severities.count("low")}
        severity_df = pd.DataFrame(list(counts.items()), columns=["Severity", "Count"]).set_index("Severity")
        st.bar_chart(severity_df)
        
        # Bug DataFrame Display
        bug_table_data = []
        for bug in st.session_state["bugs"]:
            sev = str(bug.get("severity", "low")).lower()
            if sev == "high":
                sev_display = "🔴 High"
            elif sev == "medium":
                sev_display = "🟡 Medium"
            else:
                sev_display = "🟢 Low"
                
            bug_table_data.append({
                "Line": bug.get("line_number"),
                "Type": bug.get("bug_type"),
                "Severity": sev_display,
                "Description": bug.get("description")
            })
            
        df = pd.DataFrame(bug_table_data)
        st.dataframe(df, use_container_width=True)

# =====================================================================
# Tab 3: Fix Evolution (GA)
# =====================================================================
with tab3:
    if not st.session_state["bugs"]:
        st.info("No bugs detected yet. Run analysis in 'Code Input' tab.")
    else:
        api_key = st.session_state.get("api_key", "").strip()
        if not api_key:
            st.warning("Please enter your Groq API Key in the sidebar to evolve fixes.")
        else:
            for i, bug in enumerate(st.session_state["bugs"]):
                st.subheader(f"Bug {i+1}: {bug.get('description', 'No description')}")
                key_str = str(i)
                
                if key_str in st.session_state["fixes"]:
                    saved = st.session_state["fixes"][key_str]
                    st.write(f"**Validation Score:** {saved['score']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("Original Code:")
                        st.code(st.session_state["code"], language="python")
                    with col2:
                        st.write("Fixed Code:")
                        st.code(saved["fix"], language="python")
                    st.write("Diff:")
                    st.code(saved["diff"], language="diff")
                else:
                    try:
                        with st.spinner(f"Finding/evolving fix for Bug {i+1}..."):
                            desc = bug.get('description', '')
                            fix = recall_similar_fix(desc)
                            if fix:
                                st.info(f"✨ Found matching fix in memory for Bug {i+1}!")
                            else:
                                fix = evolve_fix(
                                    st.session_state["code"],
                                    bug,
                                    api_key,
                                    generations=st.session_state["generations"],
                                    population_size=st.session_state["population_size"]
                                )
                                
                            val_res = validate_fix(st.session_state["code"], fix)
                            save_fix(desc, fix)
                            
                            saved = {
                                "fix": fix,
                                "score": val_res.get("score", 0.0),
                                "diff": val_res.get("diff", "")
                            }
                            st.session_state["fixes"][key_str] = saved
                            
                            st.write(f"**Validation Score:** {saved['score']}")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("Original Code:")
                                st.code(st.session_state["code"], language="python")
                            with col2:
                                st.write("Fixed Code:")
                                st.code(saved["fix"], language="python")
                            st.write("Diff:")
                            st.code(saved["diff"], language="diff")
                    except Exception as evolve_err:
                        st.error(f"Failed to evolve fix for Bug {i+1}: {evolve_err}")
                        continue

# =====================================================================
# Tab 4: Results & Report
# =====================================================================
with tab4:
    if not st.session_state["fixes"]:
        st.info("No fixes generated yet. Complete evolution in 'Fix Evolution (GA)' tab.")
    else:
        st.write("### Review Recommendation & Report")
        
        # Display recommendation alert
        severities = [str(bug.get('severity', '')).lower() for bug in st.session_state["bugs"]]
        if "high" in severities:
            st.error("🚨 Final Recommendation: CRITICAL")
        elif "medium" in severities:
            st.warning("⚠️ Final Recommendation: NEEDS FIX")
        else:
            st.success("✅ Final Recommendation: PASS")
            
        try:
            fix_list = [val["fix"] for val in st.session_state["fixes"].values()]
            markdown_report = generate_report(st.session_state["code"], st.session_state["bugs"], fix_list)
            st.markdown(markdown_report)
        except Exception as report_err:
            st.error(f"Failed to generate review report: {report_err}")
            
        pdf_path = "code_review_report.pdf"
        if os.path.exists(pdf_path):
            try:
                with open(pdf_path, "rb") as f:
                    pdf_data = f.read()
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_data,
                    file_name="code_review_report.pdf",
                    mime="application/pdf"
                )
            except Exception as pdf_read_err:
                st.error(f"Failed to load PDF report: {pdf_read_err}")
