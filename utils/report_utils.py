
import json
import re

def load_json_report(results):
    if isinstance(results, list):
        if len(results) == 1 and isinstance(results[0], str):
            raw_text = results[0]
        elif all(isinstance(item, dict) for item in results):
            return results
        else:
            raw_text = ''.join(results)
    elif isinstance(results, str):
        raw_text = results
    else:
        raw_text = str(results)

    raw_text = raw_text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text.removeprefix("```json").strip()
    if raw_text.endswith("```"):
        raw_text = raw_text.removesuffix("```").strip()

    try:
        arrays = re.findall(r'\[\s*{.*?}\s*\]', raw_text, re.DOTALL)
        combined = []
        for arr in arrays:
            data = json.loads(arr)
            if isinstance(data, list):
                combined.extend(data)
            else:
                combined.append(data)
        return combined

    except json.JSONDecodeError as e:
        print("❌ JSON parsing failed:", e)
        print("--- JSON Preview ---")
        print(raw_text[:500])
        raise
