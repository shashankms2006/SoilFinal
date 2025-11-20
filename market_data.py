import pandas as pd
from geopy.geocoders import Nominatim
from datetime import timedelta
import os

CSV_FILE = "9ef84268-d588-465a-a308-a864a43d0070.csv"

def fetch_prices_for_state(state: str) -> pd.DataFrame:
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()
    df = pd.read_csv(CSV_FILE)
    if "State" in df.columns:
        df_filtered = df[df["State"].str.lower() == state.lower()]
    elif "state" in df.columns:
        df_filtered = df[df["state"].str.lower() == state.lower()]
    else:
        df_filtered = pd.DataFrame()
    return df_filtered

def normalize_price_df(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "State": "state", "state": "state",
        "District": "district", "district": "district",
        "Market": "market", "market": "market",
        "Commodity": "commodity", "commodity": "commodity",
        "Variety": "variety", "variety": "variety",
        "Min_x0020_Price": "min_price", "Min_Price": "min_price", "min_price": "min_price",
        "Max_x0020_Price": "max_price", "Max_Price": "max_price", "max_price": "max_price",
        "Modal_x0020_Price": "modal_price", "Modal_Price": "modal_price", "modal_price": "modal_price",
        "Arrival_Date": "date", "arrival_date": "date", "date": "date",
    }
    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})
    for col in ["min_price", "max_price", "modal_price"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    for col in ["state", "district", "market", "commodity", "variety"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df

def get_state_from_location(query: str) -> str | None:
    geolocator = Nominatim(user_agent="soil-crop-market-system")
    q = query.strip()
    loc = None
    if q.replace(" ", "").isdigit() and 4 <= len(q.replace(" ", "")) <= 8:
        try:
            loc = geolocator.geocode({"postalcode": q, "country": "India"}, addressdetails=True, timeout=15)
        except Exception:
            loc = None
        if loc is None:
            try:
                loc = geolocator.geocode(q + ", India", addressdetails=True, timeout=15)
            except Exception:
                loc = None
    else:
        try:
            loc = geolocator.geocode(q + ", India", addressdetails=True, timeout=15)
        except Exception:
            loc = None
    if not loc:
        return None
    addr = loc.raw.get("address", {})
    state = addr.get("state") or addr.get("state_district")
    return state.strip().title() if state else None

def get_ranked_crops_for_state_from_api(state: str, days_window: int = 3) -> pd.DataFrame:
    raw_df = fetch_prices_for_state(state)
    df = normalize_price_df(raw_df)
    if "modal_price" not in df.columns:
        raise ValueError("'modal_price' column not found after normalization")
    if "date" in df.columns and not df["date"].isna().all():
        latest_date = df["date"].max()
        cutoff = latest_date - timedelta(days=days_window)
        df_recent = df[df["date"] >= cutoff].copy()
    else:
        df_recent = df.copy()
    df_recent = df_recent.dropna(subset=["modal_price"])
    df_recent = df_recent.sort_values(by=["commodity", "date", "modal_price"], ascending=[True, False, False])
    grouped = df_recent.groupby("commodity", as_index=False).first()
    keep_cols = [c for c in ["commodity", "modal_price", "date", "market", "district", "state"] if c in grouped.columns]
    result = grouped[keep_cols].copy()
    result = result.sort_values("modal_price", ascending=False).reset_index(drop=True)
    result["rank"] = result.index + 1
    order = ["rank", "commodity", "modal_price", "date", "market", "district", "state"]
    result = result[[c for c in order if c in result.columns]]
    return result

def get_ranked_crops_for_location(location_query: str, days_window: int = 3) -> pd.DataFrame:
    try:
        state = get_state_from_location(location_query)
        if not state:
            return pd.DataFrame()
        ranked = get_ranked_crops_for_state_from_api(state, days_window=days_window)
        return ranked
    except Exception:
        return pd.DataFrame()

def get_crop_price(location_query: str, crop_name: str) -> float:
    """
    Get crop price per quintal (100kg) from market data.
    Returns price as float, or 0.0 if not found.
    """
    try:
        market_df = get_ranked_crops_for_location(location_query, days_window=3)
        if market_df.empty:
            return 0.0
        # Normalize crop name for matching (handle spaces, underscores, case)
        crop_normalized = crop_name.lower().replace(" ", "_").replace("-", "_")
        match = market_df[market_df["commodity"].str.lower().str.replace(" ", "_").str.replace("-", "_") == crop_normalized]
        if not match.empty:
            return float(match.iloc[0]["modal_price"])
    except Exception:
        pass
    return 0.0
