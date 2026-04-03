"""
Quick end-to-end test for the Document Analysis API.
Run with: py test_api.py
"""
import httpx
import json

BASE_URL = "http://localhost:8000"
API_KEY = "docanalysis-k9x2m7p4q8r1n5w3"
HEADERS = {"X-API-Key": API_KEY}


def test_health():
    r = httpx.get(f"{BASE_URL}/health")
    print("✅ Health:", r.json())


def test_docx():
    with open("test_sample.docx", "rb") as f:
        r = httpx.post(
            f"{BASE_URL}/analyze",
            files={"file": ("test_sample.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            headers=HEADERS,
            timeout=60,
        )
    data = r.json()
    print("\n✅ DOCX Test:")
    print(f"  Status      : {data.get('status')}")
    print(f"  File type   : {data.get('file_type')}")
    print(f"  Word count  : {data.get('metadata', {}).get('word_count')}")
    print(f"  Proc time   : {data.get('metadata', {}).get('processing_time_ms')}ms")
    print(f"  Summary     : {data.get('analysis', {}).get('summary', '')[:120]}...")
    print(f"  Entities    : {json.dumps(data.get('analysis', {}).get('entities', []), indent=4)}")
    print(f"  Sentiment   : {data.get('analysis', {}).get('sentiment', {})}")


def test_invalid():
    import io
    r = httpx.post(
        f"{BASE_URL}/analyze",
        files={"file": ("test.xlsx", io.BytesIO(b"fake"), "application/vnd.ms-excel")},
        headers=HEADERS,
        timeout=10,
    )
    print(f"\n✅ Invalid file test (expect 400): {r.status_code} — {r.json().get('error_code')}")


def test_no_key():
    import io
    r = httpx.post(
        f"{BASE_URL}/analyze",
        files={"file": ("test.pdf", io.BytesIO(b"%PDF"), "application/pdf")},
        timeout=10,
    )
    print(f"✅ No API key test (expect 401): {r.status_code} — {r.json().get('detail', {}).get('error_code')}")


if __name__ == "__main__":
    test_health()
    test_docx()
    test_invalid()
    test_no_key()
    print("\n🎉 All tests complete!")
