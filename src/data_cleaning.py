import pandas as pd


def numericize(df):
    for col in df.columns:
        if any(token in col.lower() for token in [
            "price", "cost", "quantity", "delay", "hours", "distance",
            "tonnes", "value", "spread", "time", "rate", "kg", "inr"
        ]):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_dates(df):
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def standardize_commodity(series):
    return series.astype(str).str.strip().str.title()


def clean_datasets(datasets):
    cleaned = {}
    for name, df in datasets.items():
        if df is None or df.empty:
            cleaned[name] = df
            continue
        cleaned_df = df.copy()
        cleaned_df = clean_dates(cleaned_df)
        cleaned_df = numericize(cleaned_df)
        if "Commodity" in cleaned_df.columns:
            cleaned_df["Commodity"] = standardize_commodity(cleaned_df["Commodity"])
        if "Product" in cleaned_df.columns:
            cleaned_df["Product"] = standardize_commodity(cleaned_df["Product"])
        if "Location" in cleaned_df.columns:
            cleaned_df["Location"] = cleaned_df["Location"].astype(str).str.strip()
        if "Source" in cleaned_df.columns:
            cleaned_df["Source"] = cleaned_df["Source"].astype(str).str.strip()
        cleaned[name] = cleaned_df
    return cleaned
