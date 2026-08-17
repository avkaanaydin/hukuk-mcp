from pathlib import Path
import os
import shutil
import asyncio

import chromadb
from mcp.server import MCPServer

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DB = BASE_DIR / "hukuk_vektor_arsivi"
FALLBACK_DB = Path.home() / "Library" / "Application Support" / "Hukuk_MCP" / "hukuk_vektor_arsivi"

def choose_db_path():
    if PROJECT_DB.exists() and os.access(PROJECT_DB, os.W_OK):
        return PROJECT_DB

    FALLBACK_DB.mkdir(parents=True, exist_ok=True)

    if PROJECT_DB.exists() and any(PROJECT_DB.iterdir()):
        try:
            if not any(FALLBACK_DB.iterdir()):
                shutil.copytree(PROJECT_DB, FALLBACK_DB, dirs_exist_ok=True)
        except Exception:
            pass

    return FALLBACK_DB

DB_PATH = choose_db_path()

chroma_client = chromadb.PersistentClient(path=str(DB_PATH))
collection = chroma_client.get_or_create_collection(name="doktrin_kulliyati")

mcp = MCPServer("HukukKutuphanesi")

@mcp.tool()
async def doktrin_ara(sorgu: str) -> str:
    sonuclar = collection.query(query_texts=[sorgu], n_results=5)

    if not sonuclar.get("documents") or not sonuclar["documents"][0]:
        return "Hüküm: Kütüphanede bu hususta hukuki bulguya rastlanmamıştır."

    mutalaa = "Kütüphaneden Bulunan Hukuki Kaynaklar:\n\n"
    for i, dokuman in enumerate(sonuclar["documents"][0]):
        kaynak = sonuclar["metadatas"][0][i]["kaynak"]
        mutalaa += f"--- ESER (KAYNAK): {kaynak} ---\n{dokuman}\n\n"

    return mutalaa

async def main():
    await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
