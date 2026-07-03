import ast
import difflib

# Validates syntax of a python fix, generates a unified diff, and computes a score
def validate_fix(original: str, fix: str) -> dict:
    try:
        is_valid = True
        try:
            ast.parse(fix)
        except SyntaxError:
            is_valid = False
            
        original_lines = original.splitlines()
        fix_lines = fix.splitlines()
        
        diff_generator = difflib.unified_diff(
            original_lines,
            fix_lines,
            fromfile="original",
            tofile="fix",
            lineterm=""
        )
        diff_str = "\n".join(diff_generator)
        
        lines_changed = abs(len(original_lines) - len(fix_lines))
        
        score = 0.0
        if is_valid:
            score = 0.5
            if len(fix_lines) <= len(original_lines):
                score = 0.8
            if len(fix_lines) < len(original_lines) and len(fix) < len(original):
                score = 1.0
                
        return {
            "is_valid": is_valid,
            "diff": diff_str,
            "lines_changed": lines_changed,
            "score": score
        }
    except Exception:
        return {
            "is_valid": False,
            "diff": "",
            "lines_changed": 0,
            "score": 0.0
        }
