from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import random

app = FastAPI()

@app.post("/skill_extractor")
async def skill_extractor(request: Request):
    data = await request.json()
    batch = data.get("chunks", [])
    # Для кожного чанк генеруємо 1-2 skills (спільний dummy для всієї книжки)
    # з name-и завжди однакові для простоти мержу
    out = []
    for i, ch in enumerate(batch):
        if i % 2 == 0:
            out.append({
                "name": "Reading Comprehension",
                "evidence": [ch["chunk_id"]],
                "confidence": round(random.uniform(0.76, 0.98), 2)
            })
        else:
            out.append({
                "name": "Coreference Resolution",
                "evidence": [ch["chunk_id"]],
                "confidence": round(random.uniform(0.6, 0.87), 2)
            })
    return JSONResponse(out)

if __name__ == "__main__":
    uvicorn.run(app, port=9000, host="0.0.0.0")
