from datetime import datetime
from fpdf import FPDF

# Generates a code review report in Markdown format and saves a PDF version to disk
def generate_report(code: str, bugs: list, fixes: list) -> str:
    try:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        recommendation = "PASS"
        if bugs:
            severities = [str(bug.get('severity', '')).lower() for bug in bugs]
            if "high" in severities:
                recommendation = "CRITICAL"
            elif "medium" in severities:
                recommendation = "NEEDS FIX"
            else:
                recommendation = "PASS"
                
        md = []
        md.append("# Code Review Report")
        md.append(f"**Date:** {date_str}")
        md.append(f"**Summary:** Total bugs found: {len(bugs)}, Total fixes generated: {len(fixes)}")
        md.append(f"**Final Recommendation:** {recommendation}\n")
        
        md.append("## Bug Table")
        md.append("| Line | Type | Severity | Description |")
        md.append("| --- | --- | --- | --- |")
        for bug in bugs:
            line = bug.get('line_number', '')
            b_type = bug.get('bug_type', '')
            sev = bug.get('severity', '')
            desc = bug.get('description', '')
            md.append(f"| {line} | {b_type} | {sev} | {desc} |")
        md.append("")
        
        md.append("## Fix Details")
        for idx, fix in enumerate(fixes, 1):
            md.append(f"### Fix {idx}")
            md.append("#### Original Code")
            md.append(f"```python\n{code}\n```")
            md.append("#### Evolved Fix")
            md.append(f"```python\n{fix}\n```")
            md.append("")
            
        markdown_report = "\n".join(md)
        
        try:
            print("[DEBUG] Starting PDF generation...")
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(190, 10, "Code Review Report", 0, 1, "C")
            pdf.ln(5)
            
            pdf.set_font("helvetica", "", 12)
            pdf.cell(190, 8, f"Date: {date_str}", 0, 1)
            pdf.cell(190, 8, f"Total bugs found: {len(bugs)}", 0, 1)
            pdf.cell(190, 8, f"Total fixes generated: {len(fixes)}", 0, 1)
            pdf.cell(190, 8, f"Recommendation: {recommendation}", 0, 1)
            pdf.ln(10)
            
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(190, 8, "Bug Table", 0, 1)
            pdf.ln(2)
            
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(15, 8, "Line", 1, 0, "C")
            pdf.cell(40, 8, "Type", 1, 0, "C")
            pdf.cell(30, 8, "Severity", 1, 0, "C")
            pdf.cell(105, 8, "Description", 1, 1, "C")
            
            pdf.set_font("helvetica", "", 9)
            for bug in bugs:
                line = str(bug.get('line_number', ''))
                b_type = str(bug.get('bug_type', ''))
                sev = str(bug.get('severity', ''))
                desc = str(bug.get('description', ''))
                
                pdf.cell(15, 8, line, 1, 0, "C")
                pdf.cell(40, 8, b_type, 1, 0)
                pdf.cell(30, 8, sev, 1, 0, "C")
                pdf.cell(105, 8, desc[:60], 1, 1)
                
            pdf.output("code_review_report.pdf")
            print("[DEBUG] PDF generated successfully as 'code_review_report.pdf'")
        except Exception as pdf_error:
            print(f"[DEBUG] PDF generation failed: {pdf_error}")
            
        return markdown_report
        
    except Exception as e:
        print(f"[DEBUG] Error generating report: {e}")
        return "Report generation failed."
