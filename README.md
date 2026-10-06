# Envira loss-experience service

A small server that returns loss experience per peril for a portfolio, in DKK.

## Dependencies

- `panel`
- `pandas`
- `tornado`
- `json` (part of the Python standard library, nothing to install)

```bash
pip install panel pandas tornado
```

## Run the server

Activate an environment with the dependencies above (e.g. `conda activate Envira`).

```bash
python server.py
```

The server listens on `http://localhost:5006`. It reads the CSV files in `data/` once at startup.

Output from the server is buffered when redirected to a file; use `python -u server.py` to see the printed tables immediately.

## Get loss experience

With the server running:

```bash
curl http://localhost:5006/portfolios/PF-10/loss-experience
```

Replace `PF-10` with the portfolio id you want. The response is JSON with one row per peril:

```json
{
  "portfolio_id": "PF-10",
  "perils": [
    {
      "peril": "fire",
      "policy_count": 180,
      "earned_premium_dkk": 520927.8,
      "incurred_loss_dkk": 1183355.8,
      "loss_ratio": 2.27,
      "claim_count": 24.0,
      "largest_claim_dkk": 269418.26
    }
  ]
}
```

The table is also printed to the server console. An unknown portfolio id returns `404` with an error message.

## Summary of the work

I created a server that can accept an HTTP GET request and return the desired portfolio data. I also created a Panel interface so a non-technical user can interact with it. The data is loaded into a pandas DataFrame when the server starts, which is more efficient than reading the CSV files on every request.
