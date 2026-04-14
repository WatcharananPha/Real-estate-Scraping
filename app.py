from pathlib import Path
import logging
import datetime
from typing import Optional, Tuple, List

import pandas as pd
import duckdb
import streamlit as st

BASE_DIR = Path.cwd()
DEFAULT_CSV = BASE_DIR / "facebook" / "facebook_details.csv"
DEFAULT_PQ = BASE_DIR / "facebook" / "facebook_details.parquet"
DEFAULT_PAGE_SIZE = 25

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("app")

st.set_page_config(page_title="Facebook Listings Search", layout="wide")


@st.cache_data
def ensure_parquet(csv_path: Path, parquet_path: Path) -> Path:
    if parquet_path.exists():
        return parquet_path
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")
    df = pd.read_csv(csv_path, encoding="utf-8-sig", low_memory=False)
    if "Full_Content" in df.columns:
        df["normalized_content"] = (
            df["Full_Content"].astype(str)
            .str.lower()
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )
    if "Location" in df.columns:
        df["normalized_location"] = (
            df["Location"].astype(str)
            .str.lower()
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )
    if "Date" in df.columns:
        df["parsed_date"] = pd.to_datetime(df["Date"], errors="coerce", infer_datetime_format=True)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(parquet_path, index=False)
    except Exception:
        con_temp = duckdb.connect()
        con_temp.register("tmp_df", df)
        con_temp.execute(f"COPY (SELECT * FROM tmp_df) TO '{str(parquet_path)}' (FORMAT PARQUET)")
        con_temp.close()
    return parquet_path


@st.cache_data
def get_duckdb_conn(parquet_path: Path) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(database=":memory:")
    if parquet_path.exists():
        p = str(parquet_path).replace("'", "''")
        con.execute(f"CREATE VIEW posts AS SELECT * FROM read_parquet('{p}')")
    else:
        raise FileNotFoundError("Parquet not available")
    return con


def table_columns(con: duckdb.DuckDBPyConnection) -> List[str]:
    df = con.execute("PRAGMA table_info('posts')").fetchdf()
    return list(df["name"]) if not df.empty else []


def build_filters(columns: List[str], location: Optional[str], keyword: Optional[str],
                  date_from: Optional[datetime.date], date_to: Optional[datetime.date]) -> Tuple[str, List]:
    parts: List[str] = []
    params: List = []
    if location:
        key = "%{}%".format(location.lower())
        if "normalized_location" in columns:
            parts.append("normalized_location LIKE ?")
            params.append(key)
        elif "Full_Content" in columns:
            parts.append("LOWER(Full_Content) LIKE ?")
            params.append(key)
    if keyword:
        k = "%{}%".format(keyword.lower())
        if "Full_Content" in columns:
            parts.append("LOWER(Full_Content) LIKE ?")
            params.append(k)
    if (date_from or date_to) and "parsed_date" in columns:
        if date_from:
            parts.append("parsed_date >= ?")
            params.append(str(date_from))
        if date_to:
            params.append(str(datetime.datetime.combine(date_to, datetime.time.max)))
            parts.append("parsed_date <= ?")
    where = ("WHERE " + " AND ".join(parts)) if parts else ""
    return where, params


def query_posts(con: duckdb.DuckDBPyConnection, columns: List[str], location: Optional[str], keyword: Optional[str],
                date_from: Optional[datetime.date], date_to: Optional[datetime.date],
                page: int, page_size: int, sort_by: Optional[str]) -> Tuple[pd.DataFrame, int]:
    where, params = build_filters(columns, location, keyword, date_from, date_to)
    count_sql = f"SELECT COUNT(*) FROM posts {where}"
    total = con.execute(count_sql, params).fetchone()[0]
    offset = (page - 1) * page_size
    order = ""
    if sort_by and sort_by in columns:
        order = f"ORDER BY {sort_by} DESC"
    sql = f"SELECT * FROM posts {where} {order} LIMIT ? OFFSET ?"
    df = con.execute(sql, params + [page_size, offset]).fetchdf()
    return df, int(total)


def humanize_rows(n: int) -> str:
    if n < 1000:
        return str(n)
    return f"{n:,}"


def main():
    st.title("Facebook Listings — Search")
    left, right = st.columns([1, 3])

    with left:
        csv_input = st.text_input("CSV path", value=str(DEFAULT_CSV))
        parquet_input = st.text_input("Parquet path", value=str(DEFAULT_PQ))
        ingest = st.button("Ingest (CSV → Parquet)")
        filter_date = st.checkbox("Filter by date")
        location_q = st.text_input("Location / Area")
        keyword_q = st.text_input("Keyword")
        page_size = st.number_input("Page size", min_value=5, max_value=200, value=DEFAULT_PAGE_SIZE, step=5)
        sort_choice = st.selectbox("Sort by", options=["parsed_date", ""], index=0)
        if filter_date:
            today = datetime.date.today()
            default_from = today - datetime.timedelta(days=365)
            date_from = st.date_input("Date from", value=default_from)
            date_to = st.date_input("Date to", value=today)
        else:
            date_from = date_to = None
        if "page" not in st.session_state:
            st.session_state.page = 1
        if st.button("Search"):
            st.session_state.page = 1

    csv_path = Path(csv_input)
    parquet_path = Path(parquet_input)
    try:
        if ingest:
            ensure_parquet(csv_path, parquet_path)
            st.success("Parquet created")
        if not parquet_path.exists():
            ensure_parquet(csv_path, parquet_path)
        con = get_duckdb_conn(parquet_path)
    except Exception as exc:
        st.error(f"Dataset load failed: {exc}")
        return

    columns = table_columns(con)
    total_rows = con.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    right.header("Results")
    right.subheader(f"Rows in dataset: {humanize_rows(total_rows)}")

    df, total = query_posts(
        con=con,
        columns=columns,
        location=location_q.strip() or None,
        keyword=keyword_q.strip() or None,
        date_from=date_from,
        date_to=date_to,
        page=st.session_state.page,
        page_size=page_size,
        sort_by=sort_choice or None,
    )

    right.caption(f"Showing {len(df)} of {humanize_rows(total)} matching rows")
    right.dataframe(df.reset_index(drop=True), use_container_width=True)

    nav_col1, nav_col2, nav_col3 = right.columns([1, 1, 8])
    with nav_col1:
        if st.button("Prev") and st.session_state.page > 1:
            st.session_state.page -= 1
    with nav_col2:
        if st.button("Next") and (st.session_state.page * page_size) < total:
            st.session_state.page += 1
    with nav_col3:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download current page as CSV", data=csv_bytes, file_name="results_page.csv", mime="text/csv")

    if not df.empty:
        first_row = df.iloc[0]
        right.markdown("### First result preview")
        if "Post_URL" in first_row:
            right.markdown(f"[Open post]({first_row.get('Post_URL')})")
        if "Full_Content" in first_row:
            right.write(first_row.get("Full_Content"))
        if "Date" in first_row:
            right.write(str(first_row.get("Date")))


if __name__ == "__main__":
    main()