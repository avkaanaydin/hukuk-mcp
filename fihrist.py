import os
from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

print("Duruşma (Veri İşleme) Başlıyor. Lütfen bekleyiniz. Eserin hacmine göre bu işlem vakit alabilir...")

# 1. Veritabanı (Arşiv) Kurulumu
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "hukuk_vektor_arsivi"
MODEL_CACHE = BASE_DIR / ".cache" / "chroma" / "onnx_models" / ONNXMiniLM_L6_V2.MODEL_NAME

ONNXMiniLM_L6_V2.DOWNLOAD_PATH = MODEL_CACHE
chroma_client = chromadb.PersistentClient(path=str(DB_PATH))
collection = chroma_client.get_or_create_collection(name="doktrin_kulliyati")

# 2. Metin Bölücü (Paragraf/Fıkra ayırıcı usulü)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
    length_function=len,
)

klasor_yolu = BASE_DIR / "pdf_kulliyati"

# 3. PDF'lerin Keşfi ve İncelenmesi
for dosya_adi in sorted(os.listdir(klasor_yolu)):
    if not dosya_adi.lower().endswith(".pdf"):
        continue

    dosya_tam_yolu = os.path.join(klasor_yolu, dosya_adi)
    print(f"İncelenen Eser: {dosya_adi}")

    try:
        reader = PdfReader(dosya_tam_yolu)
        tam_metin = ""
        for sayfa in reader.pages:
            metin = sayfa.extract_text()
            if metin:
                tam_metin += metin

        if not tam_metin.strip():
            print(f"Uyarı: {dosya_adi} içeriğinde okunabilir metin bulunamadı.")
            continue

        parcalar = text_splitter.split_text(tam_metin)

        for i, parca in enumerate(parcalar):
            collection.add(
                documents=[parca],
                metadatas=[{"kaynak": dosya_adi, "fikra_no": i}],
                ids=[f"{dosya_adi}_fikra_{i}"],
            )

    except Exception as exc:
        print(f"Hata: {dosya_adi} işlenirken sorun oluştu -> {exc}")
        continue

print("HÜKÜM: Tüm işlenebilir PDF eserleri başarıyla fihristlenmiş ve yerel arşive kaydedilmiştir.")
