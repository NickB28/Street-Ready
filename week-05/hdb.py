"""Load HDB resale transactions into immutable, typed records."""

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


class DataError(Exception):
    """A problem with the input file that the user can fix."""


@dataclass(frozen=True)
class Sale:
    """One resale transaction. Frozen, so it cannot change after loading."""

    month: date
    town: str
    flat_type: str
    floor_area_sqm: Decimal
    resale_price: int


def parse_sale(row: dict[str, str]) -> Sale:
    """Turn one CSV row into a Sale. Raises ValueError (or KeyError) if a field is bad."""
    town = row["town"].strip()
    flat_type = row["flat_type"].strip()
    if not town or not flat_type:
        raise ValueError("town and flat type are required")
    month = date.fromisoformat(row["month"].strip() + "-01")
    try:
        area = Decimal(row["floor_area_sqm"])
        price = Decimal(row["resale_price"])
    except InvalidOperation:
        raise ValueError("not a number") from None
    if not area.is_finite() or area <= 0:
        raise ValueError("floor area must be positive")
    if not price.is_finite() or not 0 < price < 1_000_000_000:
        raise ValueError("price must be a positive whole number")
    if price != price.to_integral_value():
        raise ValueError("price must be a whole number")
    return Sale(month, town, flat_type, area, int(price))


def load_sales(path: Path) -> tuple[list[Sale], int]:
    """Read a resale CSV and return (sales, number of bad rows skipped)."""
    sales: list[Sale] = []
    skipped = 0
    try:
        with open(path, newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                try:
                    sales.append(parse_sale(row))
                except (KeyError, ValueError, AttributeError, TypeError):
                    skipped += 1
    except (OSError, UnicodeDecodeError, csv.Error) as err:
        reason = getattr(err, "strerror", None) or err
        raise DataError(f"cannot read {path}: {reason}") from err
    return sales, skipped