import json
from pathlib import Path
from typing import cast

from typer.testing import CliRunner

from findex.cli import app
from findex.index import build_index, save_index

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "index" in result.output
    assert "search" in result.output
    assert "stats" in result.output


def test_index_command(sample_documents: Path, tmp_path: Path) -> None:
    output = tmp_path / "index.bin"

    result = runner.invoke(
        app,
        ["index", str(sample_documents), "--out", str(output)],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert "Документів: 3" in result.output


def test_search_json_command(
    sample_documents: Path,
    tmp_path: Path,
) -> None:
    index = build_index(sample_documents)
    index_path = tmp_path / "index.bin"
    save_index(index, index_path)

    result = runner.invoke(
        app,
        [
            "search",
            "python",
            "--index-file",
            str(index_path),
            "--json",
        ],
    )

    assert result.exit_code == 0

    data = cast(list[dict[str, object]], json.loads(result.output))
    assert isinstance(data, list)
    assert len(data) > 0
    assert "doc_id" in data[0]


def test_search_missing_index(tmp_path: Path) -> None:
    missing_index = tmp_path / "missing.bin"

    result = runner.invoke(
        app,
        [
            "search",
            "python",
            "--index-file",
            str(missing_index),
        ],
    )

    assert result.exit_code == 1
    assert "індекс не знайдено" in result.output.lower()


def test_stats_command(sample_documents: Path) -> None:
    result = runner.invoke(
        app,
        ["stats", str(sample_documents)],
    )

    assert result.exit_code == 0
    assert "Статистика корпусу" in result.output
    assert "Документів" in result.output
