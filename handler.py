#!/usr/bin/env python
"""Command‑line interface for the Signal Detection System.

Usage:
    python cli.py <companies.json> [options]

Options:
    --output-json <file>   Path to write JSON results (default: signals_output.json)
    --output-sqlite <file> Path to SQLite DB (optional)
    --min-score <int>      Minimum signal score to keep (default: 0)
    --log-level <level>    Logging level (DEBUG, INFO, WARNING, ERROR)
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Project imports – these modules were created earlier in the codebase.
from signals.fetcher import fetch_rss, fetch_url
from signals.parser import parse_article
from signals.scorer import score_signal
from signals.output import write_json, write_sqlite, SignalRecord
# Project imports – these modules were created earlier in the codebase.



def load_companies(path: Path) -> list[str]:
    """Load a JSON array of company names from *path*.
    Returns a list of strings; raises a clear error if the file is missing
    or malformed.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Companies file not found: {path}")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("companies.json must contain a JSON array of strings")
    return [str(item) for item in data]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Signal Detection System")
    parser.add_argument("companies", help="Path to JSON file with a list of company names")
    parser.add_argument("--output-json", default="signals_output.json", help="JSON output file")
    parser.add_argument("--output-sqlite", help="SQLite DB output file (optional)")
    parser.add_argument("--min-score", type=int, default=0, help="Minimum signal score to retain")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    args = parser.parse_args(argv)

    # Configure logging early
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    )

    try:
        companies = load_companies(Path(args.companies))
    except Exception as e:
        logging.error("Failed to load companies: %s", e)
        return 1

    all_signals = []
    for company in companies:
        logging.info("Processing company: %s", company)
        try:
            rss_entries = fetch_rss(company)
            for entry in rss_entries:
                link = entry.get('link')
                if not link:
                    continue
                raw_html = fetch_url(link)
                parsed = parse_article(raw_html)
                # Convert numeric strings (with possible commas) to ints
                numbers = []
                for num_str in parsed.get('numeric_signals', []):
                    try:
                        numbers.append(int(num_str.replace(',', '')))
                    except ValueError:
                        continue
                score, reason = score_signal(parsed.get('keywords', []), numbers)
                if score >= args.min_score:
                    record = SignalRecord(
                        company=company,
                        signal_type='mass_hiring_signal',
                        source_url=link,
                        matched_keywords=parsed.get('keywords', []),
                        signal_score=score,
                        detected_at=datetime.utcnow().isoformat(),
                        reason=reason,
                    )
                    all_signals.append(record)
        except Exception as exc:
            logging.warning("Error processing %s: %s", company, exc)

    # Write outputs
    write_json(all_signals, Path(args.output_json))
    logging.info("Wrote %d signals to %s", len(all_signals), args.output_json)
    if args.output_sqlite:
        write_sqlite(all_signals, Path(args.output_sqlite))
        logging.info("Also stored signals in SQLite DB %s", args.output_sqlite)

    return 0

if __name__ == "__main__":
    sys.exit(main())
