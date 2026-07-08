from pathlib import Path

from src.etl.inventory_datasus import build_inventory, classify_file, default_output_for, write_markdown_inventory


def test_inventory_marks_current_2024_sources_as_present():
    rows = build_inventory([2024])
    by_source = {row.source: row for row in rows}

    assert by_source["SINAN/SIFCBR"].status == "presente"
    assert by_source["SINASC"].status == "presente"
    assert by_source["CNES/ST"].status == "presente"
    assert by_source["SIM/DO"].status == "presente"


def test_inventory_marks_core_sources_as_required():
    rows = build_inventory([2024], scope="core")

    assert {row.source for row in rows} == {"SINAN/SIFCBR", "SINASC"}
    assert {row.priority for row in rows} == {"obrigatorio"}


def test_inventory_exposes_target_paths_for_missing_historical_files():
    rows = build_inventory([2014], scope="all")
    by_source = {row.source: row for row in rows}

    assert by_source["SINAN/SIFCBR"].expected_file == "SIFCBR14.dbc"
    assert by_source["SINAN/SIFCBR"].target_path.replace("\\", "/") == "data/raw/sinan/sifilis_congenita/SIFCBR14.dbc"
    assert by_source["CNES/ST"].priority == "complementar"


def test_inventory_markdown_lists_missing_required_and_complementary_files(tmp_path):
    rows = [row for row in build_inventory([2014], scope="all") if row.status == "ausente"]
    output = tmp_path / "datasus_missing_files.md"

    write_markdown_inventory(rows, output)

    content = output.read_text(encoding="utf-8")
    assert "SIFCBR14.dbc" in content
    assert "DNRS2014.dbc" in content
    assert "STRS1412.dbc" in content
    assert "DORS2014.dbc" in content
    assert "data/raw/sinan/sifilis_congenita/SIFCBR14.dbc" in content


def test_inventory_default_output_matches_format():
    assert default_output_for("csv").name == "datasus_inventory.csv"
    assert default_output_for("markdown").name == "datasus_inventory.md"


def test_classify_file_marks_dnex_as_out_of_scope():
    row = classify_file(Path("data/ignored/DNEX2024.dbc"))

    assert row.base == "SINASC"
    assert row.uf == "EX"
    assert row.status == "fora_de_escopo"


def test_classify_file_marks_cnes_december_rs_snapshot():
    row = classify_file(Path("data/raw/cnes/st/STRS2412.dbc"))

    assert row.base == "CNES"
    assert row.ano == "2024"
    assert row.uf == "RS"
    assert row.tipo == "st_mes_12"
    assert row.status == "disponivel"


def test_classify_file_marks_population_files_as_complementary():
    row = classify_file(Path("data/raw/populacao_datasus/pop24.dbf"))

    assert row.base == "Populacao DATASUS"
    assert row.ano == "2024"
    assert row.tipo == "populacao_residente"
