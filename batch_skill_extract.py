import requests
import json
from typing import List, Dict, Any
import random, string

# === CONFIGURE THESE ===
BOOK_ID = "dummy-book-v2"  # Тестовий BookID
BACKEND_URL = "http://localhost:8000"
CTX_WRITE_ENDPOINT = f"{BACKEND_URL}/ctx/write"
CTX_READ_ENDPOINT = f"{BACKEND_URL}/ctx/read"  # Для перевірки
LLM_ENDPOINT = "http://localhost:9000/skill_extractor"  # Мок-LLM
BATCH_SIZE = 6

# Функція локального чанк-генератора (dummy data)
def local_generate_chunks(book_id: str, n=12) -> List[Dict[str, Any]]:
    base_rules = [
        "Define single responsibility principle in 1 sentence.",
        "List steps of clean code refactoring.",
        "Describe object inheritance in one rule.",
        "Give an example of dependency inversion.",
        "Explain testable design briefly.",
        "Clarify separation of concerns in OOP.",
        "State the open/closed principle.",
        "Provide the concept of class composition.",
        "Summarize interface segregation.",
        "List reasons for unit testing.",
        "Describe code readability impact.",
        "Give a definition to code coupling.",
    ]
    # Mix in some noise for variety
    chunks = []
    for i in range(n):
        c_id = f"chunk_{i+1}"
        txt = f"CHUNK {i+1}. {base_rules[i % len(base_rules)]}"
        # стиснута симуляція: обрізати до суті і видалити шум
        compressed = txt.replace("in one rule", "(OOP): ...")
        chunks.append({
            "chunk_id": c_id,
            "book_id": book_id,
            "text_content": compressed
        })
    return chunks

def batch_chunks(chunks: List[Dict[str, Any]], batch_size: int):
    for i in range(0, len(chunks), batch_size):
        yield chunks[i:i + batch_size]


def compress_chunk_text(chunk: Dict[str, Any]) -> str:
    # Dummy: already короткі у local_generate_chunks
    return " ".join(chunk["text_content"].split())


def call_llm_for_skills(batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    batch_objs = [{
        "chunk_id": c["chunk_id"],
        "text": compress_chunk_text(c)
    } for c in batch]
    payload = {
        "chunks": batch_objs,
        "instruction": (
            "Extract every unique skill found in these chunks. "
            "Output only JSON in the format: ["
            "{\"name\": <skill name>, \"evidence\": [<chunk_id>], \"confidence\": <float>}]. "
            "Combine evidence if a skill is present in several chunks. "
            "No summary or explanation. Output ONLY the JSON."
        )
    }
    resp = requests.post(LLM_ENDPOINT, json=payload)
    if not resp.ok:
        raise Exception(f"LLM batch extraction failed: {resp.status_code} {resp.text}")
    # Should be valid JSON (list of {name, evidence, confidence})
    return resp.json()


def merge_skills(skills_batches: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    merged = {}
    for batch in skills_batches:
        for skill in batch:
            key = skill["name"].strip()
            if key not in merged:
                merged[key] = {
                    "name": skill["name"].strip(),
                    "evidence": set(skill["evidence"]),
                    "confidence": skill["confidence"]
                }
            else:
                merged[key]["evidence"].update(skill["evidence"])
                merged[key]["confidence"] = max(merged[key]["confidence"], skill["confidence"])
    # Convert sets back to lists
    for v in merged.values():
        v["evidence"] = list(v["evidence"])
    return list(merged.values())


def upload_skills(book_id: str, skills: List[Dict[str, Any]]):
    payload = {
        "book_id": book_id,
        "data": {"skills": skills}
    }
    resp = requests.post(CTX_WRITE_ENDPOINT, json=payload)
    print("Upload status:", resp.status_code, resp.text)
    if not resp.ok:
        raise Exception(f"Failed to upload skills: {resp.status_code} {resp.text}")


def confirm_skills(book_id: str):
    query_payload = {"query": "*", "top_k": 50}
    resp = requests.post(CTX_READ_ENDPOINT, json=query_payload)
    if not resp.ok:
        print(f"/ctx/read failed: {resp.status_code} {resp.text}")
        return
    print("=== /ctx/read result ===")
    print(json.dumps(resp.json(), indent=2))


def main():
    print(f"Generating compressed chunks for test book_id={BOOK_ID} ...")
    chunks = local_generate_chunks(BOOK_ID, n=12)
    print(f"Generated {len(chunks)} chunks. Batching...")
    skills_batches = []
    for i, batch in enumerate(batch_chunks(chunks, BATCH_SIZE)):
        print(f"Processing batch {i+1} ({len(batch)} chunks)...")
        skills = call_llm_for_skills(batch)
        print(f"- Extracted {len(skills)} skills from batch {i+1}")
        skills_batches.append(skills)
    print(f"Merging skills from {len(skills_batches)} batches...")
    merged_skills = merge_skills(skills_batches)
    print(f"Merged to {len(merged_skills)} unique skills. Uploading...")
    upload_skills(BOOK_ID, merged_skills)
    print("Skill extraction complete! Total unique skills:", len(merged_skills))
    confirm_skills(BOOK_ID)

if __name__ == "__main__":
    main()
