# Hukuk MCP

Yerel hukuk kütüphanenizi Claude veya MCP destekleyen diğer yapay zeka istemcilerine
açan, Türkçe hukuk metinleri için geliştirilmiş bir Model Context Protocol (MCP)
sunucusudur.

PDF'leriniz bilgisayarınızda kalır. Sistem metni çıkarır, anlamlı parçalara böler ve
ChromaDB üzerinde yerel vektör araması oluşturur. Sorulara dönen sonuçlarda kullanılan
PDF adı ve ilgili metin parçası birlikte gösterilir.

## Öne Çıkanlar

- Tamamen yerel PDF arşivi ve ChromaDB vektör veritabanı
- Türkçe hukuk metinlerinde anlamsal arama
- Yeni veya değişen PDF'leri otomatik indeksleme
- MCP uyumlu istemcilerle standart bağlantı
- PDF değişikliklerini yaklaşık 5 saniyede algılayan arka plan izleyicisi
- Başarısız veya metinsiz PDF'leri atlayıp sonraki taramada tekrar deneyebilme

## Nasıl Çalışır?

```text
pdf_kulliyati/  ->  pypdf  ->  metin parçaları  ->  ChromaDB  ->  MCP istemcisi
                                      ^
                         yeni PDF'ler otomatik izlenir
```

## Gereksinimler

- macOS 12 veya üzeri
- Python 3.11 veya üzeri
- Git
- MCP destekleyen bir istemci: Claude Desktop veya ChatGPT'nin MCP/Developer Mode'u

## macOS Kurulumu

Terminal'i açın ve aşağıdaki komutları sırayla çalıştırın:

```bash
git clone https://github.com/avkaanaydin/hukuk-mcp.git
cd hukuk-mcp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
mkdir -p pdf_kulliyati
```

Kurulumun çalıştığını doğrulayın:

```bash
./.venv/bin/python -m py_compile fihrist.py pdf_indeksleyici.py mcp_sunucusu.py
```

## PDF Kütüphanesini Hazırlama

Hukuki PDF dosyalarınızı `pdf_kulliyati/` klasörüne kopyalayın. İlk indekslemeyi
başlatmak için:

```bash
source .venv/bin/activate
python fihrist.py
```

İlk çalıştırma, PDF sayısına ve embedding modelinin ilk indirilmesine bağlı olarak
uzun sürebilir. İndeks durumu `processed_pdfs.json` ile takip edilir; aynı dosya tekrar
işlenmez. Değiştirilen bir PDF'nin eski parçaları silinir ve yeni içeriğiyle yazılır.

## Claude Desktop'a Bağlama

Önce proje klasörünün tam yolunu öğrenin:

```bash
cd /path/to/hukuk-mcp
pwd
```

Claude Desktop yapılandırma dosyasını terminalden açın:

```bash
mkdir -p "$HOME/Library/Application Support/Claude"
nano "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

Dosyaya aşağıdaki JSON'u ekleyin. `/path/to/hukuk-mcp` bölümünü `pwd` çıktınızla
değiştirin:

```json
{
  "mcpServers": {
    "hukuk_kutuphanesi": {
      "command": "/path/to/hukuk-mcp/.venv/bin/python",
      "args": [
        "/path/to/hukuk-mcp/mcp_sunucusu.py"
      ]
    }
  }
}
```

Claude Desktop'ı tamamen kapatıp yeniden açın. MCP bağlantısı kurulduğunda
`doktrin_ara` aracı kullanılabilir hale gelir.

## ChatGPT ile Kullanım

ChatGPT bağlantı adımları kullanılan ChatGPT uygulamasına, hesaba ve MCP/Developer
Mode erişimine göre değişebilir. ChatGPT sürümünüz yerel STDIO MCP sunucularını
destekliyorsa, yeni bir MCP uygulaması/bağlantısı eklerken şu komut ve argümanları
kullanın:

```text
Komut: /path/to/hukuk-mcp/.venv/bin/python
Argüman: /path/to/hukuk-mcp/mcp_sunucusu.py
```

ChatGPT arayüzü JSON yapılandırması kabul ediyorsa Claude örneğindeki `mcpServers`
bloğu kullanılabilir. MCP seçeneği görünmüyorsa bu, proje hatası değildir; kullandığınız
ChatGPT istemcisi veya hesap türü yerel STDIO MCP bağlantısını etkinleştirmiyor olabilir.
Bu durumda MCP destekleyen bir istemci kullanın veya ChatGPT'nin güncel resmi MCP/
Developer Mode yönergelerindeki bağlantı yöntemini izleyin.

## Otomatik PDF Güncelleme

MCP sunucusu açıkken tek yapmanız gereken yeni dosyayı kopyalamaktır:

```bash
cp ~/Downloads/yeni_kanun.pdf /path/to/hukuk-mcp/pdf_kulliyati/
```

Sunucu klasörü yaklaşık 5 saniyede bir kontrol eder. Yeni PDF otomatik olarak
indekslenir ve sonraki aramalarda kullanılabilir. Manuel olarak `fihrist.py` çalıştırmak
veya istemciyi yeniden başlatmak gerekmez.

MCP sunucusu kapalıyken PDF eklediyseniz, sunucu açıldığında bekleyen dosyalar otomatik
olarak indekslenir. Manuel alternatif:

```bash
cd /path/to/hukuk-mcp
source .venv/bin/activate
python fihrist.py
```

## Manuel Test

MCP sunucusunu doğrudan çalıştırmak için:

```bash
cd /path/to/hukuk-mcp
./.venv/bin/python mcp_sunucusu.py
```

Bu komut STDIO üzerinden çalışan bir sunucudur; terminalde normal bir web sayfası
göstermemesi beklenir. Kullanım için Claude Desktop veya MCP destekleyen bir istemci
üzerinden bağlanın.

## Veri ve Gizlilik

- PDF'ler, ChromaDB veritabanı ve embedding modeli yerel bilgisayarınızda tutulur.
- `pdf_kulliyati/`, `hukuk_vektor_arsivi/`, `.venv/` ve `.cache/` GitHub'a gönderilmez.
- Telif hakkı ve kişisel veri içeren belgeleri paylaşırken ilgili izinleri kontrol edin.
- `processed_pdfs.json` yerel işlem durumudur ve GitHub'a gönderilmez.

## Lisans

Bu proje kişisel kullanım ve geliştirme amacıyla sunulmuştur. Lisans koşulları için
repository sahibine danışın.
