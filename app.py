#!/usr/bin/env python3
"""
Directory Finder - Standalone Web Service
-----------------------------------------
Automated nursing faculty directory URL discovery and live validation.
Powered by Gemini 3.5 Flash-Lite & curated institution registry.
"""

import os
import sys
import tempfile
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Ensure local directory is in Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Load environment variables
dotenv_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

# Import finder engine
from finder import (
    find_directory_for_school,
    extract_schools_from_text,
    extract_schools_from_pdf,
    extract_schools_from_excel,
    deduplicate_school_names
)

# Initialize FastAPI App
app = FastAPI(
    title="Nursing Directory Finder",
    description="Locates and live-validates official Nursing Faculty & Staff Directory URLs",
    version="1.0.0"
)

# Enable CORS for all clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INDEX_HTML_PATH = os.path.join(BASE_DIR, "index.html")
if not os.path.isfile(INDEX_HTML_PATH):
    parent_index = os.path.join(os.path.dirname(BASE_DIR), "index.html")
    if os.path.isfile(parent_index):
        INDEX_HTML_PATH = parent_index

# Health Check Endpoint
@app.get("/api/health")
@app.get("/health")
def health_check():
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    return {
        "status": "online",
        "service": "Directory Finder",
        "model": "gemini-3.5-flash-lite",
        "gemini_configured": bool(gemini_key)
    }

# Request schema for directory discovery
class DirectorySearchRequest(BaseModel):
    schools: Optional[List[str]] = Field(default=[], description="List of institution names")
    text: Optional[str] = Field(default="", description="Raw pasted text containing institution names")
    concurrency: Optional[int] = Field(default=5, description="Number of concurrent discovery workers")

# Main Directory Discovery Endpoint
@app.post("/api/find-directories")
@app.post("/find-directories")
def find_directories_endpoint(payload: DirectorySearchRequest):
    schools = []
    if payload.text and payload.text.strip():
        schools.extend(extract_schools_from_text(payload.text))
    if payload.schools:
        schools.extend(payload.schools)

    schools = deduplicate_school_names(schools)
    if not schools:
        raise HTTPException(status_code=400, detail="No valid school names provided.")

    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    workers = min(max(payload.concurrency, 1), 10)
    results = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(find_directory_for_school, s, gemini_key): s for s in schools}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                s_name = futures[future]
                results.append({
                    "school": s_name,
                    "directory_url": "",
                    "status": f"Error: {e}",
                    "is_ready_for_extractor": False
                })

    # Deduplicate results by normalized directory URL and school name
    deduped = []
    seen_urls = set()
    seen_schools = set()
    for r in results:
        u = (r.get("directory_url") or "").rstrip('/').lower()
        s = (r.get("school") or "").strip().lower()
        if u and u in seen_urls:
            continue
        if s and s in seen_schools:
            continue
        if u:
            seen_urls.add(u)
        if s:
            seen_schools.add(s)
        deduped.append(r)

    results = deduped
    results.sort(key=lambda x: x.get("school", ""))
    verified_count = sum(1 for r in results if r.get("is_ready_for_extractor"))

    return {
        "success": True,
        "total": len(results),
        "verified_count": verified_count,
        "results": results
    }

# File Upload Extraction Endpoint (PDF, Excel, CSV, TXT)
@app.post("/api/extract-schools-from-file")
@app.post("/extract-schools-from-file")
async def extract_schools_from_file_endpoint(file: UploadFile = File(...)):
    content = await file.read()
    fname = (file.filename or "upload").lower()

    suffix = os.path.splitext(fname)[1] or ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=tempfile.gettempdir()) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        if fname.endswith(".pdf"):
            schools = extract_schools_from_pdf(tmp_path)
        elif fname.endswith((".xlsx", ".xls", ".csv")):
            schools = extract_schools_from_excel(tmp_path)
        else:
            text = content.decode("utf-8", errors="ignore")
            schools = extract_schools_from_text(text)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    return {
        "filename": file.filename,
        "count": len(schools),
        "schools": schools
    }

# Serve Directory Finder Frontend UI
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/index.html", response_class=HTMLResponse, include_in_schema=False)
def serve_ui():
    if os.path.isfile(INDEX_HTML_PATH):
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(
            content=content,
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    raise HTTPException(status_code=404, detail="Directory Finder UI not found")

if __name__ == "__main__":
    import uvicorn
    # Default port 8001 so it does not conflict with Contact Finder on 8000
    print("[*] Starting Directory Finder server on http://127.0.0.1:8001 ...")
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
