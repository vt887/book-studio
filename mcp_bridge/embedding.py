import hashlib


def deterministic_embedding(text: str, dim: int) -> list[float]:
    normalized = (text or "").strip().lower()
    if not normalized:
        return [0.0] * dim

    vec = [0.0] * dim
    for token in normalized.split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for i in range(dim):
            b = digest[i % len(digest)]
            vec[i] += (b / 255.0) - 0.5

    norm = sum(v * v for v in vec) ** 0.5
    if norm == 0.0:
        return [0.0] * dim
    return [v / norm for v in vec]
