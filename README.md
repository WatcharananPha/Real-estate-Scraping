# Real-estate-Scraping

รวมสคริปต์และโน้ตบุ๊กสำหรับดึงข้อมูลอสังหาริมทรัพย์จาก Facebook และเว็บไซต์ประกาศ (Kaidee, LivingInsider, Propertyhub, Thailand-Property, ฯลฯ)

## สรุปงาน

- Phase 1: Facebook group scrapers (เก็บ Post URLs, ข้อมูลโพสต์เบื้องต้น)
- Phase 2: Portal scrapers (หลายโน้ตบุ๊กใน `web-scraping/`) และ AI classification (Typhoon) อยู่ใน `ai.ipynb`
- Phase 3: Handover — รวบรวมโค้ดและ CSV

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
