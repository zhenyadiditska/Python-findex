# findex — Лабораторні роботи 1 і 2

## Опис проєкту

Цей проєкт — програма для аналізу текстових документів, написана мовою Python.

Мета роботи — навчитися працювати з генераторами, ітераторами, потоковою обробкою даних, структурами даних та інвертованим індексом.

Програма читає текстові документи, розділяє їх на токени, збирає статистику та створює інвертований індекс, за допомогою якого можна шукати документи за словами.

## Текстовий корпус

Корпус містить 1218 текстових документів загальним розміром приблизно 25 MB.

Джерела документації:

- Python 3.14: https://docs.python.org/3.14/
- Django 6.0: https://docs.djangoproject.com/

Також до корпусу додано кілька власних тестових документів.

Папка `data/` виключена з Git за допомогою `.gitignore`.

## Структура проєкту

```text
findex/
├── data/
├── src/
│   └── findex/
│       ├── __init__.py
│       ├── corpus.py
│       ├── tokenize.py
│       ├── stats.py
│       ├── greedy.py
│       ├── index.py
│       ├── search.py
│       └── memory.py
├── tests/
│   ├── test_tokenize.py
│   └── test_search.py
├── README.md
├── pyproject.toml
├── uv.lock
└── .gitignore
```

## Лабораторна робота 1 — Аналіз текстового корпусу

### Правила токенізації

Для нормалізації тексту використовується Unicode NFC та метод `casefold()`.

Основні правила:

- Усі слова переводяться в нижній регістр.
- Розділові знаки ігноруються.
- Апострофи всередині слів зберігаються.
- Дефіси всередині слів зберігаються.
- Цифри можуть бути частиною токенів.
- Символ підкреслення вважається роздільником.

Приклади:

- `Python` → `python`
- `front-end` → `front-end`
- `don't` → `don't`
- `Python3` → `python3`
- `web_dev` → `web`, `dev`

### Запуск аналізу

Потокова версія:

```bash
uv run python -m findex.stats
```

Версія з попереднім завантаженням даних:

```bash
uv run python -m findex.greedy
```

### Порівняння продуктивності

Обидві версії перевірялися на однаковому корпусі.

| Показник                   |    Streaming |        Greedy |
| -------------------------- | -----------: | ------------: |
| Кількість документів       |         1218 |          1218 |
| Загальна кількість токенів |    2 857 461 |     2 857 461 |
| Унікальні токени           |       56 895 |        56 895 |
| Час виконання              |   5.286473 с |    4.076011 с |
| Пікова пам'ять             | 38 205.19 KB | 179 987.69 KB |

### Висновки

Потокова версія обробляє документи по одному та не зберігає всі документи й токени у списках.

Greedy-версія спочатку завантажує всі документи та токени в пам'ять. Через це вона використовує значно більше ресурсів.

Під час тестування Greedy-версія працювала швидше, але використовувала приблизно у 4,7 раза більше пам'яті.

Отже, потокова обробка є ефективнішою з погляду використання пам'яті, особливо під час роботи з великими текстовими корпусами.

## Лабораторна робота 2 — Інвертований індекс

### Побудова індексу

У другій лабораторній роботі було реалізовано інвертований індекс.

Він зберігає інформацію про те, в яких документах зустрічається певне слово та скільки разів воно там з'являється.

Для зберігання даних використовуються два класи:

- `Posting` — містить ідентифікатор документа та частоту слова.
- `DocMeta` — містить ідентифікатор документа, шлях до нього та кількість токенів.

Обидва класи створені за допомогою `dataclass(frozen=True, slots=True)`.

Індекс будується за один прохід через документи. Для збирання частот використовується `defaultdict` разом із `Counter`. Списки postings для кожного слова сортуються за ідентифікатором документа.

### Boolean-пошук

Реалізовано три логічні операції:

- `AND` — знаходить документи, в яких є обидва слова.
- `OR` — знаходить документи, в яких є хоча б одне з двох слів.
- `NOT` — знаходить документи, в яких є перше слово, але немає другого.

Для пошуку реалізовано два способи:

1. `merge` — порівняння двох відсортованих списків за допомогою двох покажчиків.
2. `set` — використання множин для пошуку спільних або різних документів.

За замовчуванням використовується `merge`. Також можна вибрати потрібний алгоритм за допомогою параметра `--engine`.

### Збереження індексу

Для збереження та завантаження індексу реалізовано два формати:

- `pickle` — зберігає об'єкти Python у бінарному файлі `index.bin`.
- JSON — зберігає дані у текстовому файлі `index.json`.

Формат JSON зручний тим, що його можна переглянути звичайним текстовим редактором. Файл `pickle` займає менше місця та швидше завантажується в проведеному тесті.

Важливо: файли `pickle` не можна завантажувати з невідомих або ненадійних джерел

## Lab 03 — Ranking and Object Model

### 1. Model indeksu

Klasa `Index` udostępnia:
- `__len__`, `__contains__`, `__getitem__`, `__iter__`, `__repr__`
- `num_docs`, `avg_doc_length`, `doc_length()` i `df()`
- `open_index()` jako context manager.

### 2. Ranking

Zaimplementowano dwa algorytmy:
- TF-IDF
- BM25 z parametrami `k1=1.5` i `b=0.75`.

Wyniki są przechowywane w `SearchResult`, a najlepsze dokumenty wybierane przez `heapq.nlargest()`.

### 3. Parser zapytań

Parser obsługuje:
- AND, OR i NOT
- niejawne AND między sąsiednimi terminami
- nawiasy
- wyszukiwanie fraz w cudzysłowie.

Przykład:

`python AND (async OR await) NOT java "event loop"`

### 4. Cache, dekoratory i snippets

- `@timed` mierzy czas wykonywania funkcji.
- `lru_cache(maxsize=256)` przechowuje wyniki zapytań.
- `make_snippet()` tworzy fragment tekstu i wyróżnia znalezione słowa.

### 5. Eksperymenty z rankingiem

Indeks zawiera 1218 dokumentów i 56895 unikalnych terminów.

Przeprowadzono trzy testy:

1. Rzadki termin `flask` (DF=1) uzyskał wyższą ocenę niż częsty termin `in` (DF=1176).
2. W BM25 różnica ocen między 19. a 20. powtórzeniem terminu wyniosła około 0.00011.
3. Dla terminu `models`, występującego po jednym razu w obu dokumentach, krótki документ uzyskał ocenę 2.7183, a długi — 0.0244.

### 6. Precision@5

Przeprowadzono ocenę 10 zapytań z ręcznie określoną релевантністю документів.

| Zapytanie | TF-IDF | BM25 |
|---|---:|---:|
| python | 0.80 | 1.00 |
| django | 1.00 | 1.00 |
| async | 1.00 | 1.00 |
| database | 1.00 | 1.00 |
| security | 0.60 | 1.00 |
| testing | 0.80 | 0.60 |
| template | 1.00 | 1.00 |
| request | 0.60 | 1.00 |
| class AND method | 0.80 | 1.00 |
| "event loop" | 0.60 | 0.80 |
| **Średnia** | **0.82** | **0.94** |

W tym eksperymencie BM25 uzyskał wyższy średni Precision@5 niż TF-IDF. Wyniki zależą od ręcznej oceny trafności dokumentów.
