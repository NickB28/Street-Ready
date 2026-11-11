import dataclasses
from decimal import Decimal
from pathlib import Path

import pytest
from hdb import DataError, Sale, load_sales

SAMPLE = Path(__file__).parent.parent / "data" / "sample.csv"
HEADER = (
    "month,town,flat_type,block,street_name,storey_range,floor_area_sqm,"
    "flat_model,lease_commence_date,remaining_lease,resale_price"
)


def make_row(
    month: str = "2017-01", town: str = "ANG MO KIO", area: str = "44", price: str = "232000"
) -> str:
    """Build one full CSV row, changing only the fields a test cares about."""
    return f"{month},{town},2 ROOM,406,ANG MO KIO AVE 10,10 TO 12,{area},Improved,1979,61 years,{price}"


def write_csv(tmp_path: Path, *rows: str, encoding: str = "utf-8") -> Path:
    """Write a CSV with the real header plus the given rows."""
    path = tmp_path / "sales.csv"
    path.write_text(HEADER + "\n" + "\n".join(rows) + "\n", encoding=encoding)
    return path


def test_sample_file_loads() -> None:
    sales, skipped = load_sales(SAMPLE)
    assert len(sales) + skipped == 5000
    assert len(sales) > 0


def test_record_fields_have_the_right_types(tmp_path: Path) -> None:
    sales, skipped = load_sales(write_csv(tmp_path, make_row()))
    assert skipped == 0
    sale = sales[0]
    assert sale.month.year == 2017 and sale.month.month == 1
    assert sale.floor_area_sqm == Decimal("44")
    assert isinstance(sale.resale_price, int)
    assert sale.resale_price == 232000


def test_bad_rows_are_counted_not_fatal(tmp_path: Path) -> None:
    path = write_csv(
        tmp_path,
        make_row(),
        make_row(price="abc"),
        make_row(area="-5"),
        make_row(town=""),
        make_row(month="2017-13"),
        make_row(price="232000.5"),
        "2017-01,ANG MO KIO",
    )
    sales, skipped = load_sales(path)
    assert len(sales) == 1
    assert skipped == 6


def test_price_written_as_a_whole_float_is_accepted(tmp_path: Path) -> None:
    sales, skipped = load_sales(write_csv(tmp_path, make_row(price="232000.0")))
    assert skipped == 0
    assert sales[0].resale_price == 232000


def test_file_saved_with_a_utf8_bom_is_accepted(tmp_path: Path) -> None:
    sales, skipped = load_sales(write_csv(tmp_path, make_row(), encoding="utf-8-sig"))
    assert len(sales) == 1
    assert skipped == 0


def test_missing_file_raises_data_error(tmp_path: Path) -> None:
    with pytest.raises(DataError, match="cannot read"):
        load_sales(tmp_path / "nope.csv")


def test_sale_is_immutable(tmp_path: Path) -> None:
    sale = load_sales(write_csv(tmp_path, make_row()))[0][0]
    assert isinstance(sale, Sale)
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(sale, "town", "BEDOK")