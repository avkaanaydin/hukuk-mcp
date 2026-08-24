import json
import os
import sys
import tempfile
from pathlib import Path
from threading import Lock

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

PROCESSED_FILE = Path(__file__).resolve().parent / "processed_pdfs.json"
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
    length_function=len,
)
index_lock = Lock()


def _file_signature(pdf_path: Path) -> dict:
    stat = pdf_path.stat()
    return {"size": stat.st_size, "modified_ns": stat.st_mtime_ns}


def _load_processed() -> dict:
    if not PROCESSED_FILE.exists():
        return {}
    try:
        data = json.loads(PROCESSED_FILE.read_text(encoding="utf-8"))
        processed = data.get("processed_files", {})
        if isinstance(processed, list):
            return {}
        return processed
    except (json.JSONDecodeError, OSError):
        return {}


def _save_processed(processed: dict) -> None:
    payload = {
        "processed_files": processed,
        "last_update": __import__("datetime").datetime.now().isoformat(),
    }
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=PROCESSED_FILE.parent, delete=False
    ) as temporary_file:
        json.dump(payload, temporary_file, ensure_ascii=False, indent=2)
        temporary_path = Path(temporary_file.name)
    temporary_path.replace(PROCESSED_FILE)


def index_pdf(pdf_path: Path, collection) -> bool:
    """Index one PDF and return whether it was successfully processed."""
    try:
        reader = PdfReader(str(pdf_path))
        full_text = "".join(page.extract_text() or "" for page in reader.pages)
        if not full_text.strip():
            print(f"Uyarı: {pdf_path.name} okunabilir metin içermiyor.", file=sys.stderr)
            return False

        chunks = text_splitter.split_text(full_text)
        collection.delete(where={"kaynak": pdf_path.name})
        collection.add(
            documents=chunks,
            metadatas=[{"kaynak": pdf_path.name, "fikra_no": i} for i in range(len(chunks))],
            ids=[f"{pdf_path.name}_fikra_{i}" for i in range(len(chunks))],
        )
        return True
    except Exception as exc:
        print(f"Hata: {pdf_path.name} işlenirken sorun oluştu -> {exc}", file=sys.stderr)
        return False


def index_pending_pdfs(pdf_folder: Path, collection) -> list[str]:
    """Index new or changed PDFs and record their signatures."""
    pdf_folder.mkdir(parents=True, exist_ok=True)
    processed = _load_processed()
    indexed = []

    with index_lock:
        for pdf_path in sorted(pdf_folder.glob("*.pdf")):
            signature = _file_signature(pdf_path)
            if processed.get(pdf_path.name) == signature:
                continue

            print(f"İncelenen Eser: {pdf_path.name}", file=sys.stderr)
            if index_pdf(pdf_path, collection):
                processed[pdf_path.name] = signature
                indexed.append(pdf_path.name)

        existing_names = {path.name for path in pdf_folder.glob("*.pdf")}
        for file_name in set(processed) - existing_names:
            del processed[file_name]
        _save_processed(processed)

    return indexed