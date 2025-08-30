import os, re, json

def analyze_file(path: str) -> dict:
    """Very simple heuristic 'AI pre-check' placeholder.
    - For .txt files: basic token stats + naive 'long words' count
    - For other types: mark as 'not analyzed in demo'
    """
    name = os.path.basename(path)
    report = {
        "filename": name,
        "type": "generic",
        "summary": "Basic pre-check completed.",
        "stats": {},
        "notes": []
    }
    if path.lower().endswith(".txt"):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            tokens = re.findall(r"[A-Za-z']+", text)
            long_words = [t for t in tokens if len(t) >= 12]
            ratio_letters = sum(ch.isalpha() for ch in text) / max(1, len(text))
            report["type"] = "text"
            report["stats"] = {
                "tokens": len(tokens),
                "unique_tokens": len(set(tokens)),
                "long_words": len(long_words),
                "letters_ratio": round(ratio_letters, 3)
            }
            if len(long_words) > 20:
                report["notes"].append("High count of long words — check for spacing or typos.")
            if ratio_letters < 0.6:
                report["notes"].append("Low letters ratio — file may include many symbols or be poorly scanned.")
        except Exception as e:
            report["summary"] = f"Error reading text: {e}"
    else:
        report["summary"] = "Non-text file: demo pre-check limited (no OCR)."
    return report
