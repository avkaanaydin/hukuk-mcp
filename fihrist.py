from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from pdf_indeksleyici import index_pending_pdfs

print("Duruşma (Veri İşleme) Başlıyor. Lütfen bekleyiniz...", flush=True)

# 1. Veritabanı (Arşiv) Kurulumu
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "hukuk_vektor_arsivi"
MODEL_CACHE = BASE_DIR / ".cache" / "chroma" / "onnx_models" / ONNXMiniLM_L6_V2.MODEL_NAME

ONNXMiniLM_L6_V2.DOWNLOAD_PATH = MODEL_CACHE
chroma_client = chromadb.PersistentClient(path=str(DB_PATH))
collection = chroma_client.get_or_create_collection(name="doktrin_kulliyati")

klasor_yolu = BASE_DIR / "pdf_kulliyati"

index_pending_pdfs(klasor_yolu, collection)

print("HÜKÜM: Tüm işlenebilir PDF eserleri başarıyla fihristlenmiş ve yerel arşive kaydedilmiştir.")
