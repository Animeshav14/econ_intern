import os
import pandas as pd
from typing import Dict

REQUIRED_COLUMNS = ["Internship Title", "Company", "Link", "Location", "Eligible Majors"]

def _load_csv(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    # Normalize columns
    df.columns = [c.strip() for c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Sheet missing columns: {missing}. Found: {list(df.columns)}")
    # Clean rows
    df = df.dropna(subset=["Internship Title", "Company", "Link"]).reset_index(drop=True)
    return df

def load_industry_sheets() -> Dict[str, pd.DataFrame]:
    """
    Reads CSV links from env. Each tab has its own CSV export link.
    Add more later by extending INDUSTRY_LIST and matching *_SHEET_CSV env vars.
    """
    industries = [s.strip() for s in os.getenv("INDUSTRY_LIST", "Finance,Research").split(",") if s.strip()]
    store = {}
    for name in industries:
        key = f"{name.upper()}_SHEET_CSV"
        url = os.getenv(key)
        if not url:
            # skip silent if missing to let you add later
            continue
        try:
            df = _load_csv(url)
            store[name] = df
        except Exception as e:
            # propagate clear error
            raise RuntimeError(f"Failed to load {name} from {key}: {e}")
    if not store:
        raise RuntimeError("No industry sheets loaded. Check INDUSTRY_LIST and the *_SHEET_CSV env vars.")
    return store
