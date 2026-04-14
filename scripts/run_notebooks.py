#!/usr/bin/env python3
"""Execute a list of Jupyter notebooks sequentially and save executed copies."""
import logging
import time
import traceback
from pathlib import Path
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

NOTEBOOKS = [
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/facebook/facebook_scraping.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/9asset/9asset.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/BaanFinder/BaanFinder.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/baania/baania.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/dotproperty/dotproperty.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/ennxo/ennxo.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/fazwaz/fazwaz.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/hipflat/hipflat.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/kaidee/kaidee.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/livinginsider/livinginsider.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/propertyhub/propertyhub.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/terrabkk/terrabkk.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/thailand-property/thailand-property.ipynb",
    "/home/kongla/Documents/GitHub/Real-estate-Scraping/web-scraping/zmyhome/zmyhome.ipynb",
]

TIMEOUT = 600  # seconds per notebook
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "executed_notebooks"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def execute_notebook(path: str) -> bool:
    nb_path = Path(path)
    if not nb_path.exists():
        logging.error("Notebook not found: %s", nb_path)
        return False
    logging.info("Starting execution: %s", nb_path)
    try:
        nb = nbformat.read(str(nb_path), as_version=4)
        ep = ExecutePreprocessor(timeout=TIMEOUT, kernel_name="python3")
        ep.preprocess(nb, {"metadata": {"path": str(nb_path.parent)}})
        out_path = OUTPUT_DIR / (nb_path.stem + ".executed.ipynb")
        nbformat.write(nb, str(out_path))
        logging.info("Saved executed notebook: %s", out_path)
        return True
    except Exception as exc:
        logging.error("Error executing %s: %s", nb_path, exc)
        logging.debug(traceback.format_exc())
        return False


def main():
    total = len(NOTEBOOKS)
    succeeded = 0
    for idx, nb in enumerate(NOTEBOOKS, start=1):
        logging.info("(%d/%d) %s", idx, total, nb)
        start = time.time()
        ok = execute_notebook(nb)
        elapsed = time.time() - start
        if ok:
            succeeded += 1
            logging.info("Completed in %.1fs", elapsed)
        else:
            logging.warning("Failed after %.1fs", elapsed)

    logging.info("Run finished: %d succeeded, %d failed", succeeded, total - succeeded)


if __name__ == "__main__":
    main()
