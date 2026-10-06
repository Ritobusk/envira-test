from pathlib import Path

import pandas as pd

DATA_DIR: Path = Path(__file__).parent / "data"

PAID_ONLY: set[str] = {"settled", "closed"}
OPEN: set[str] = {"open", "reopened"}

Tables = dict[str, pd.DataFrame]


def _text(s: pd.Series) -> pd.Series:
    return s.astype("string").str.strip()


def _dates(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, format="mixed", dayfirst=True, errors="coerce")


def load_data(data_dir: str | Path = DATA_DIR) -> Tables:
    data_dir = Path(data_dir)
    assets = pd.read_csv(data_dir / "assets.csv")
    policies = pd.read_csv(data_dir / "policies.csv")
    claims = pd.read_csv(data_dir / "claims.csv")
    fx = pd.read_csv(data_dir / "fx_rates.csv")

    for df in (assets, policies, claims, fx):
        for col in df.select_dtypes(include=["object", "string"]):
            df[col] = _text(df[col])

    policies["peril"] = policies["peril"].str.lower()
    policies["status"] = policies["status"].str.lower()
    claims["status"] = claims["status"].str.lower()
    for df in (policies, claims, fx):
        df["currency"] = df["currency"].str.upper()

    for col in ("inception_date", "expiry_date"):
        policies[col] = _dates(policies[col])
    for col in ("loss_date", "reported_date"):
        claims[col] = _dates(claims[col])

    assets = assets.drop_duplicates("asset_id")
    policies = policies.drop_duplicates("policy_id")
    claims = claims.drop_duplicates("claim_id")

    fx["month"] = pd.PeriodIndex(fx["month"], freq="M")
    fx = fx.drop_duplicates(["month", "currency"], keep="last")

    return {"assets": assets, "policies": policies, "claims": claims, "fx": fx}


def _to_dkk(df: pd.DataFrame, amount_cols: list[str], month_col: str, fx: pd.DataFrame) -> pd.DataFrame:
    rates = fx.set_index(["currency", "month"])["rate_dkk_per_unit"]
    months = df[month_col].dt.to_period("M")
    idx = pd.MultiIndex.from_arrays([df["currency"], months])
    rate = pd.Series(rates.reindex(idx).to_numpy(), index=df.index)
    out = df.copy()
    for col in amount_cols:
        out[col + "_dkk"] = out[col] * rate
    return out


def incurred(claims: pd.DataFrame) -> pd.Series:
    status = claims["status"]
    paid = claims["paid_amount"].fillna(0)
    reserve = claims["reserve_amount"].fillna(0)
    total = pd.Series(0.0, index=claims.index)
    total[status.isin(PAID_ONLY)] = paid
    total[status.isin(OPEN)] = paid + reserve
    return total


def build_policy_table(data: Tables) -> pd.DataFrame:
    """One row per valid policy, with DKK premium, DKK incurred loss and claim count."""
    assets, policies, claims, fx = (data[k] for k in ("assets", "policies", "claims", "fx"))

    policies = policies[policies["asset_id"].isin(assets["asset_id"])]
    policies = policies.merge(assets[["asset_id", "portfolio_id", "region", "asset_type"]], on="asset_id")
    policies = _to_dkk(policies, ["annual_premium"], "inception_date", fx)

    claims = claims[claims["policy_id"].isin(policies["policy_id"])].copy()
    claims["incurred"] = incurred(claims)
    claims = _to_dkk(claims, ["incurred"], "loss_date", fx)
    claims = claims[claims["incurred_dkk"].notna()]

    per_policy = claims.groupby("policy_id").agg(
        incurred_dkk=("incurred_dkk", "sum"),
        claim_count=("claim_id", "count"),
        largest_claim_dkk=("incurred_dkk", "max"),
    )
    policies = policies.merge(per_policy, on="policy_id", how="left")
    policies[["incurred_dkk", "claim_count", "largest_claim_dkk"]] = policies[
        ["incurred_dkk", "claim_count", "largest_claim_dkk"]
    ].fillna(0)
    return policies.dropna(subset=["annual_premium_dkk"])


def loss_experience(policy_table: pd.DataFrame, portfolio_id: str) -> pd.DataFrame:
    p = policy_table[policy_table["portfolio_id"] == portfolio_id]
    by_peril = p.groupby("peril").agg(
        policy_count=("policy_id", "count"),
        earned_premium_dkk=("annual_premium_dkk", "sum"),
        incurred_loss_dkk=("incurred_dkk", "sum"),
        claim_count=("claim_count", "sum"),
        largest_claim_dkk=("largest_claim_dkk", "max"),
    )
    by_peril["loss_ratio"] = by_peril["incurred_loss_dkk"] / by_peril["earned_premium_dkk"]
    return by_peril.reset_index()
