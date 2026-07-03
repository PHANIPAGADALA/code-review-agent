import ast
import json
from groq import Groq

# Cleans markdown code fences and language specifiers from raw response text
def _clean_code(text: str) -> str:
    cleaned = text.replace("```python", "").replace("```PYTHON", "").replace("```", "").strip()
    if cleaned.lower().startswith("python"):
        cleaned = cleaned[6:].strip()
    return cleaned

# Calculates the quality score of a fix compared to the original code
def score_fix(original: str, fix: str) -> float:
    try:
        ast.parse(fix)
    except SyntaxError:
        return 0.0
        
    score = 1.0
    original_lines = len(original.splitlines())
    fix_lines = len(fix.splitlines())
    if fix_lines < original_lines:
        score += 0.3
        
    if len(fix) < len(original):
        score += 0.2
        
    return score

# Performs crossover by combining the first half of fix1 lines with the second half of fix2 lines
def crossover(fix1: str, fix2: str) -> str:
    lines1 = fix1.splitlines()
    lines2 = fix2.splitlines()
    
    half1 = len(lines1) // 2
    half2 = len(lines2) // 2
    
    combined = "\n".join(lines1[:half1] + lines2[half2:])
    try:
        ast.parse(combined)
        return combined
    except SyntaxError:
        return fix1

# Mutates a fix slightly using Groq
def mutate(fix: str, api_key: str) -> str:
    print("[DEBUG] Mutating fix candidate with Groq...")
    try:
        client = Groq(api_key=api_key)
        prompt = (
            "Improve this Python fix slightly. \n"
            "Return only the improved code. No explanation.\n\n"
            f"Code:\n{fix}"
        )
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return _clean_code(response.choices[0].message.content)
    except Exception as e:
        print(f"[DEBUG] Error mutating fix: {e}")
        return fix

# Evolves candidate bug fixes over multiple generations using genetic algorithm operators with Groq
def evolve_fix(code: str, bug: dict, api_key: str, generations: int = 3, population_size: int = 4) -> str:
    first_candidate = None
    try:
        print("[DEBUG] Initializing Groq client for initial population...")
        client = Groq(api_key=api_key)
        
        population = []
        for i in range(population_size):
            try:
                prompt = (
                    f"Fix the following bug in this Python code:\n"
                    f"Bug description: {bug.get('description', '')}\n"
                    f"Line number: {bug.get('line_number', 'unknown')}\n"
                    f"Bug type: {bug.get('bug_type', 'unknown')}\n\n"
                    f"Code:\n{code}\n\n"
                    "Return only the corrected Python code. No explanation. No markdown."
                )
                print(f"[DEBUG] Generating candidate {i + 1}/{population_size} using Groq...")
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                candidate = _clean_code(response.choices[0].message.content)
                if first_candidate is None:
                    first_candidate = candidate
                population.append(candidate)
            except Exception as e:
                print(f"[DEBUG] Failed to generate candidate {i + 1}: {e}")
                
        if not population:
            print("[DEBUG] Zero candidates generated. Returning original code.")
            return code
            
        for gen in range(1, generations + 1):
            print(f"[DEBUG] Starting generation {gen}...")
            scored_pop = []
            for j, candidate in enumerate(population):
                score = score_fix(code, candidate)
                print(f"Generation {gen}, Candidate {j + 1}: score={score}")
                scored_pop.append((score, candidate))
                
            scored_pop.sort(key=lambda x: x[0], reverse=True)
            
            if population_size < 2:
                cutoff = len(scored_pop)
            else:
                cutoff = max(2, len(scored_pop) // 2)
            
            survivors = [cand for score, cand in scored_pop[:cutoff]]
            print(f"[DEBUG] Generation {gen}: Kept {len(survivors)} survivors.")
            
            new_population = []
            idx = 0
            while len(new_population) < population_size:
                s1 = survivors[idx % len(survivors)]
                s2 = survivors[(idx + 1) % len(survivors)]
                idx += 2
                
                child = crossover(s1, s2)
                mutated_child = mutate(child, api_key)
                new_population.append(mutated_child)
                
            population = new_population
            
        print("[DEBUG] Scoring final population...")
        final_scored = []
        for j, candidate in enumerate(population):
            score = score_fix(code, candidate)
            print(f"Generation {generations + 1}, Candidate {j + 1}: score={score}")
            final_scored.append((score, candidate))
            
        final_scored.sort(key=lambda x: x[0], reverse=True)
        return final_scored[0][1]
        
    except Exception as e:
        print(f"[DEBUG] Unhandled error during evolution: {e}")
        if first_candidate is not None:
            return first_candidate
        return code
