from pathlib import Path
import os
import shutil
import asyncio

import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from mcp.server import MCPServer
from pdf_indeksleyici import index_pending_pdfs

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DB = BASE_DIR / "hukuk_vektor_arsivi"
FALLBACK_DB = Path.home() / "Library" / "Application Support" / "Hukuk_MCP" / "hukuk_vektor_arsivi"
MODEL_CACHE = BASE_DIR / ".cache" / "chroma" / "onnx_models" / ONNXMiniLM_L6_V2.MODEL_NAME
PDF_FOLDER = BASE_DIR / "pdf_kulliyati"

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

ONNXMiniLM_L6_V2.DOWNLOAD_PATH = MODEL_CACHE
chroma_client = chromadb.PersistentClient(path=str(DB_PATH))
collection = chroma_client.get_or_create_collection(name="doktrin_kulliyati")

mcp = MCPServer("HukukKutuphanesi")

@mcp.tool()
async def doktrin_ara(sorgu: str) -> str:
    sonuclar = collection.query(query_texts=[sorgu], n_results=5)

    belgeler = sonuclar.get("documents")
    metadatalar = sonuclar.get("metadatas")
    if not belgeler or not belgeler[0]:
        return "Hüküm: Kütüphanede bu hususta hukuki bulguya rastlanmamıştır."

    mutalaa = "Kütüphaneden Bulunan Hukuki Kaynaklar:\n\n"
    bulunan_kaynak = False
    for i, dokuman in enumerate(belgeler[0]):
        metadata = metadatalar[0][i] if metadatalar and metadatalar[0] else None
        if not dokuman or not metadata:
            continue

        kaynak = metadata.get("kaynak", "Bilinmeyen kaynak")
        mutalaa += f"--- ESER (KAYNAK): {kaynak} ---\n{dokuman}\n\n"
        bulunan_kaynak = True

    if bulunan_kaynak:
        return mutalaa

    return "Hüküm: Kütüphanede bu hususta hukuki bulguya rastlanmamıştır."

async def pdf_klasorunu_izle():
    while True:
        await asyncio.to_thread(index_pending_pdfs, PDF_FOLDER, collection)
        await asyncio.sleep(5)

async def main():
    izleyici = asyncio.create_task(pdf_klasorunu_izle())
    try:
        await mcp.run_stdio_async()
    finally:
        izleyici.cancel()
        await asyncio.gather(izleyici, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
