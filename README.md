# Directory Finder (Standalone Service)

Automated university nursing faculty directory discovery & live URL validator.
Powered by **Gemini 3.5 Flash-Lite** & state board report parsers.

---

### Features
1. **Document Ingestion**: Upload state nursing regulatory PDFs (e.g. `cna-training-prog.pdf`, State Board NCLEX pass rates), Excel sheets (`.xlsx`, `.csv`), or paste institution names directly.
2. **Intelligent Deduplication & Degree Stripping**: Automatically removes degree program qualifiers (BSN, RN, Associates) and table noise (license numbers, addresses, emails, phone numbers).
3. **5 Simultaneous Parallel Workers**: Resolves institutions and candidate directory links with 5 concurrent threads for fast batch processing.
4. **Live HTTP Verification**: Tests candidate URLs to eliminate 404s, detect Cloudflare/Wordfence firewalls, and verify directory markers.
5. **Clean Multi-Format Exports**:
   - Download CSV spreadsheet (`.csv`)
   - Download Excel spreadsheet (`.xlsx`)
   - Export clean URLs list (`.txt`)
   - One-click copy URLs to clipboard
6. **Full Clear All**: Instant one-click reset for inputs, uploads, tables, metrics, and logs.

---

### Quick Start

#### Option 1: Double-click `start.bat` (Windows)
Double-click `start.bat` to launch the server and automatically open the UI at `http://127.0.0.1:8001`.

#### Option 2: Run via Terminal
```powershell
cd directory_finder
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```
Then visit: `http://127.0.0.1:8001` in your browser.

#### Option 3: Command Line CLI
```powershell
python finder.py --file "path/to/schools.pdf" --output "verified_urls.xlsx"
```
