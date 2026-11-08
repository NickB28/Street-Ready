"""Make week-05/data/sample.csv: an evenly spread 5,000-row sample of the full file."""

from pathlib import Path

DATA = Path(__file__).parent / "data"
TARGET_ROWS = 5000


def main() -> None:
    """Copy the header and every Nth row of resale_full.csv into sample.csv."""
    with open(DATA / "resale_full.csv", encoding="utf-8-sig", newline="") as source:
        lines = source.read().splitlines()
    header, rows = lines[0], lines[1:]
    step = max(1, len(rows) // TARGET_ROWS)
    chosen = rows[::step][:TARGET_ROWS]
    with open(DATA / "sample.csv", "w", encoding="utf-8", newline="") as target:
        target.write("\n".join([header, *chosen]) + "\n")
    print(f"wrote {len(chosen)} rows (every {step}th) to {DATA / 'sample.csv'}")


if __name__ == "__main__":
    main()