import json
import logging
from collections import Counter
from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from findex.corpus import iter_documents
from findex.index import build_index, save_index
from findex.index_model import open_index
from findex.query import parse_query
from findex.scoring import BM25, TfIdf
from findex.search import collect_terms, rank_documents
from findex.snippets import make_snippet
from findex.tokenize import tokenize

app = typer.Typer(
    help="Пошукова система Findex",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)

console = Console()
progress_console = Console(stderr=True)


@app.callback()
def configure_logging(
    verbose: Annotated[
        int,
        typer.Option("-v", count=True, help="Збільшити рівень деталізації"),
    ] = 0,
) -> None:
    if verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        force=True,
    )


@app.command()
def index(
    data_dir: Annotated[
        Path,
        typer.Argument(help="Папка з текстовими документами"),
    ] = Path("data"),
    output: Annotated[
        Path,
        typer.Option("--out", "-o", help="Файл для збереження індексу"),
    ] = Path("index.bin"),
) -> None:
    if not data_dir.is_dir():
        typer.echo(f"Помилка: папку не знайдено: {data_dir}", err=True)
        raise typer.Exit(code=1)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=progress_console,
        ) as progress:
            task = progress.add_task("Створення індексу...", total=None)
            result = build_index(data_dir)
            save_index(result, output)
            progress.update(task, description="Індекс збережено")

        console.print(f"Документів: {result.num_docs}")
        console.print(f"Унікальних термінів: {len(result)}")
        console.print(f"Файл: {output}")

    except OSError as error:
        typer.echo(f"Помилка роботи з файлами: {error}", err=True)
        raise typer.Exit(code=1) from error


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Пошуковий запит")],
    index_file: Annotated[
        Path,
        typer.Option("--index-file", "-i"),
    ] = Path("index.bin"),
    scorer: Annotated[
        Literal["tfidf", "bm25"],
        typer.Option("--scorer", "-s"),
    ] = "tfidf",
    top_k: Annotated[
        int,
        typer.Option("--top-k", "-k", min=1),
    ] = 10,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Вивести результати у форматі JSON"),
    ] = False,
) -> None:
    if not index_file.is_file():
        typer.echo(f"Помилка: індекс не знайдено: {index_file}", err=True)
        raise typer.Exit(code=1)

    try:
        with open_index(index_file) as loaded_index:
            tree = parse_query(query)

            selected_scorer = BM25() if scorer == "bm25" else TfIdf()
            results = rank_documents(
                query,
                loaded_index,
                scorer=selected_scorer,
                top_k=top_k,
            )

            terms = collect_terms(tree)

            if json_output:
                data = [
                    {
                        "doc_id": result.doc_id,
                        "score": result.score,
                        "title": result.title,
                    }
                    for result in results
                ]
                typer.echo(json.dumps(data, ensure_ascii=False, indent=2))
                return

            table = Table(title=f"Результати пошуку: {query}")
            table.add_column("№", justify="right")
            table.add_column("Документ")
            table.add_column("Оцінка", justify="right")
            table.add_column("Фрагмент")

            for number, result in enumerate(results, start=1):
                document = loaded_index.documents[result.doc_id]

                snippet = make_snippet(
                    document.path,
                    terms,
                    window=80,
                )

                table.add_row(
                    str(number),
                    result.doc_id,
                    f"{result.score:.4f}",
                    snippet,
                )

            console.print(table)

    except (OSError, ValueError) as error:
        typer.echo(f"Помилка: {error}", err=True)
        raise typer.Exit(code=1) from error


@app.command()
def stats(
    data_dir: Annotated[
        Path,
        typer.Argument(help="Папка з текстовими документами"),
    ] = Path("data"),
) -> None:
    if not data_dir.is_dir():
        typer.echo(f"Помилка: папку не знайдено: {data_dir}", err=True)
        raise typer.Exit(code=1)

    counter: Counter[str] = Counter()
    document_count = 0
    total_tokens = 0

    try:
        for document in iter_documents(data_dir):
            document_count += 1
            tokens = list(tokenize(document.text))
            counter.update(tokens)
            total_tokens += len(tokens)

    except OSError as error:
        typer.echo(f"Помилка читання документів: {error}", err=True)
        raise typer.Exit(code=1) from error

    table = Table(title="Статистика корпусу")
    table.add_column("Показник")
    table.add_column("Значення", justify="right")

    table.add_row("Документів", str(document_count))
    table.add_row("Усього токенів", str(total_tokens))
    table.add_row("Унікальних термінів", str(len(counter)))

    console.print(table)

    top_table = Table(title="Топ 10 термінів")
    top_table.add_column("Термін")
    top_table.add_column("Кількість", justify="right")

    for word, count in counter.most_common(10):
        top_table.add_row(word, str(count))

    console.print(top_table)


if __name__ == "__main__":
    app()