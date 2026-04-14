# Real-estate-Scraping

รวมสคริปต์และโน้ตบุ๊กสำหรับดึงข้อมูลอสังหาริมทรัพย์จาก Facebook และเว็บไซต์ประกาศ (Kaidee, LivingInsider, Propertyhub, Thailand-Property, ฯลฯ)

## สรุปงาน

- Phase 1: Facebook group scrapers (เก็บ Post URLs, ข้อมูลโพสต์เบื้องต้น) — มีใน `facebook/facebook_scraping.ipynb` และ CSV ผลลัพธ์
- Phase 2: Portal scrapers (หลายโน้ตบุ๊กใน `web-scraping/`) และ AI classification (Typhoon) อยู่ใน `ai.ipynb`
- Phase 3: Handover — รวบรวมโค้ดและ CSV; ยังขาด README/runner (ไฟล์นี้ + `run_all.py`) และเอกสารรันแบบละเอียด

## Prerequisites

- Python 3.9+ (แนะนำ 3.10+)
- Chrome บนเครื่อง และ `undetected-chromedriver` (ดู `requirements.txt`)

1. Create venv and install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# If you plan to use notebook runner conversion:
pip install jupyter
```

1. Environment variables (ตั้งใน `.env` หรือ export):

- `TYPHOON_API_KEY` — (optional) สำหรับเรียก Typhoon model (ใช้ใน `ai.ipynb`)
- `FACEBOOK_EMAIL`, `FACEBOOK_PASSWORD` — (optional) ถ้าต้องการให้สคริปต์ล็อกอินอัตโนมัติ

1. Chrome profile: repository ใช้โฟลเดอร์ `chrome_profile` เป็นค่าเริ่มต้น (สร้างอัตโนมัติเมื่อเรียกงาน)

## ไฟล์ที่สำคัญ

- Facebook scrapers: `facebook/facebook_scraping.ipynb`
- Facebook outputs: `facebook/Facebook_post_urls.csv`, `facebook/facebook_details.csv`
- Portal scrapers: `web-scraping/*/*.ipynb` (เช่น `web-scraping/kaidee/kaidee.ipynb`)
- AI / classification: `ai.ipynb`
- Runner (ออโต้ช่วยแปลงและรันโน้ตบุ๊ก): `run_all.py`

## How to run

- Run a notebook interactively (recommended for development):

```bash
jupyter notebook facebook/facebook_scraping.ipynb
```

- Use the runner to convert notebooks to scripts and optionally execute them.

List available tasks:

```bash
python run_all.py --list
```

Convert-only (dry-run of conversion):

```bash
python run_all.py facebook-groups --convert-only
```

Convert and execute (run the converted script):

```bash
python run_all.py facebook-groups --run
```

Run all known notebooks (convert + run):

```bash
python run_all.py all --run
```

Notes:

- `run_all.py` uses `jupyter nbconvert --to script` to produce `.py` files, so `jupyter`/`nbconvert` must be installed.
- Some notebooks include multiple `if __name__ == '__main__'` blocks; review the converted `.py` before running in production.

## Outputs

- Facebook group URLs: `facebook/Facebook_post_urls.csv`
- Facebook post-details: `facebook/facebook_details.csv`
- Portal outputs: `web-scraping/*/*_full_details.csv`

## Next recommended steps

1. Integrate `ai.ipynb` classification into scrapers to output structured fields (price, area, property_type, poster_type).
1. Add README run instructions per-site and a small wrapper to run scrapers in background/cron.
1. Add basic tests and a short handover document.

---

If you want, I can now wire the Typhoon classification into the Facebook post-detail pipeline or create a minimal `runner` service to run scrapers sequentially and resume on failure.