# Hukuk MCP

Türk hukuk metinleri üzerinde arama yapan bir Model Context Protocol (MCP) sunucusudur.

Bu proje, yerel PDF kütüphanesindeki hukuki metinleri ayrıştırır, chunk'lara böler ve Chroma DB üzerinde arama yapılabilir hale getirir.

## Özellikler

- PDF klasöründen metin çıkarma
- ChromaDB ile vektör tabanlı arama
- Claude Desktop için MCP sunucu desteği
- Hukuki kaynaklara dayalı sonuç döndürme

## Gereksinimler

- Python 3.11+
- Git

## Kurulum

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## PDF İndeksleme

```bash
python fihrist.py
```

Bu komut, `pdf_kulliyati/` klasöründeki PDF’leri işler ve Chroma veritabanına ekler.

## MCP Sunucusunu Çalıştırma

```bash
python mcp_sunucusu.py
```

## Claude Desktop için config örneği

Aşağıdaki JSON örneğini kendi bilgisayarınızın gerçek yolu ile düzenleyin:

```json
{
  "mcpServers": {
    "hukuk_kutuphanesi": {
      "command": "/absolute/path/to/your/python",
      "args": [
        "/absolute/path/to/your/project/mcp_sunucusu.py"
      ]
    }
  }
}
```

Örnek:

```json
{
  "mcpServers": {
    "hukuk_kutuphanesi": {
      "command": "/Users/yourname/projects/hukuk-mcp/.venv/bin/python",
      "args": [
        "/Users/yourname/projects/hukuk-mcp/mcp_sunucusu.py"
      ]
    }
  }
}
```

> Dikkat: Bu dosyada kullanıcıya ait mutlak path yazılmalıdır. GitHub’a push ederken bu path’i sabit olarak commit etmeyin.

## Yeni PDF Ekleme

1. Yeni PDF’yi `pdf_kulliyati/` klasörüne koyun.
2. Ardından indexleme komutunu yeniden çalıştırın:

```bash
python fihrist.py
```

## Notlar

- Veritabanı klasörü `hukuk_vektor_arsivi/` kişisel yerel veritabanıdır.
- Büyük dosya ve veritabanı içerikleri GitHub’a eklenmemelidir.

## Lisans

Bu proje kişisel kullanım ve geliştirme için tasarlanmıştır.
