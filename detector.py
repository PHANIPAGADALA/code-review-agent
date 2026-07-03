import json
from groq import Groq

# Analyzes Python code for bugs using the Groq API with model openai/gpt-oss-120b
def detect_bugs(code: str, api_key: str) -> list:
    print("[DEBUG] Starting bug detection with Groq...")
    try:
        print("[DEBUG] Creating Groq client...")
        client = Groq(api_key=api_key)
        
        system_content = "You are a senior Python code reviewer."
        user_content = (
            "Review this Python code and return ONLY a \n"
            "valid JSON array. No explanation. No markdown.\n"
            "Each item must have exactly these keys:\n"
            "line_number, bug_type, description, severity\n"
            "Severity must be: high, medium, or low\n\n"
            f"Code:\n{code}"
        )
        
        print("[DEBUG] Sending code to Groq (model: openai/gpt-oss-120b)...")
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ]
        )
        
        print("[DEBUG] Extracting raw response content...")
        raw_content = response.choices[0].message.content
        print(f"[DEBUG] Raw response content: {raw_content}")
        
        print("[DEBUG] Stripping markdown fences and json identifiers...")
        cleaned_content = raw_content.replace("```json", "").replace("```JSON", "").replace("```", "").strip()
        if cleaned_content.lower().startswith("json"):
            cleaned_content = cleaned_content[4:].strip()
            
        print("[DEBUG] Parsing JSON content...")
        parsed_list = json.loads(cleaned_content)
        
        print("[DEBUG] Bug detection completed successfully.")
        return parsed_list
        
    except Exception as e:
        print(f"[DEBUG] Error occurred: {e}")
        return []
