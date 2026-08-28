# Extra prompts

> **Public repo:** do **not** commit production `shop.db` (customer-like contact data). Authoritative policy: README + `*.db` in `.gitignore`. The homework text below may say to include the DB; for a public submission that instruction does not apply.

Все user-промпты эксперимента + вспомогательные вопросы агента при подготовке спеки.

«Файл с дополнительными промптами» — это этот файл: что человек отправил сверх исходного брифа, и какие уточняющие вопросы понадобились, чтобы спека стала однозначной.

Итого user-промптов: **30** (system follow-up «Briefly inform…» не считаются).

---

## 1. Prep / MCP cheat sheet — промпт 1

```
What do you know about mcp? Cookbook, best practicies, standradrts?
```

## 2. Prep / MCP cheat sheet — промпт 2

```
What do you think about this?
"docs/MCP_Cheat_Sheet_2026.xlsx"
```

## 3. Prep / MCP cheat sheet — промпт 3

```
Could you convert it to md file?
```

## 4. Prep / MCP cheat sheet — промпт 4

```
Please run an agent to evaluate that md file
```

## 5. Prep / MCP cheat sheet — промпт 5

```
How is it going?
```

## 6. Prep / MCP cheat sheet — промпт 6

```
I think it's stucked on awaiting approval of fetching url
```

## 7. Prep / MCP cheat sheet — промпт 7

```
Continue from the place you have stucked
```

## 8. Prep / MCP cheat sheet — промпт 8

```
Please make suggested edits
```

## 9. Prep / MCP cheat sheet — промпт 9

```
Run eval again
```

## 10. Prep / MCP cheat sheet — промпт 10

```
Yes, repeat iteration, don't make the mistakes that we seen before and don't make the changes that lead to mistakes or already be done. Don't repeat ideas that didn't work. Be consecutive.
```

## 11. Prep / MCP cheat sheet — промпт 11

```
please proceed
```

## 12. Prep / MCP cheat sheet — промпт 12

```
Eval?
```

## 13. Spec prepare — промпт 1

````
We need to work on the following task:
```txt
Домашнее задание: Создание MCP-сервера для работы с базой данных
Цель
Создать MCP-сервер, который позволит AI-агенту работать с базой данных интернет-магазина.
Вы получите готовую SQLite-базу данных с информацией о клиентах, товарах и заказах.
Ваша задача — сделать MCP-сервер, подключить его к AI-агенту и добиться того, чтобы агент мог самостоятельно отвечать на вопросы по данным.
Можно использовать Python или Node.js.
Главное ограничение
Код MCP-сервера нельзя писать вручную.
Вы должны использовать AI coding agent для создания MCP-сервера.
Можно использовать:

Claude Code

Codex

 Cursor

Gemini CLI

другой AI coding agent
Можно использовать интернет, документацию и MCP SDK.
1. База данных
Вам предоставляется SQLite database:
shop.db 
База содержит следующие сущности:

customers — клиенты

products — товары

orders — заказы

order_items — товары внутри заказов
Схема базы:
customers     │     └──< orders              │              └──< order_items >── products 
База является read-only.
Ваш MCP не должен изменять данные.
2. Требования к MCP
Создайте MCP-сервер, который работает через stdio.
Он должен запускаться локально примерно так:
{   "command": "python",   "args": ["/absolute/path/to/server.py"] } 
или:
{   "command": "node",   "args": ["/absolute/path/to/server.js"] } 
MCP должен самостоятельно подключаться к shop.db.
Не требуйте от пользователя запускать отдельный HTTP-сервер.
3. Что должен уметь MCP
Вы самостоятельно решаете, какие MCP tools необходимы.
Однако подключённый AI-агент должен быть способен выполнять следующие задачи.
Задача 1
Show me all available tables and explain what information each table contains.
Задача 2
How many customers are from Germany?
Задача 3
Which country has the most customers?
Агент должен вернуть страну и количество клиентов.
Задача 4
Who is the customer who spent the most money?
Агент должен определить клиента на основе заказов и вернуWho is the customer who spent the most money?ть:

имя;

email;

общую сумму покупок.
Задача 5
What are the top 5 best-selling products?
Для каждого товара показать:

название;

количество проданных единиц;

revenue.
Задача 6
What are the top 3 product categories by revenue?
Агент должен самостоятельно связать:
orders → order_items → products 
и выполнить необходимую агрегацию.
Задача 7
How much revenue did we generate in 2025?
Учитывать только соответствующие заказы.
Задача 8
Which customer placed the most orders?
Вернуть клиента и количество заказов.
4. Safety requirement
MCP должен предоставлять только read-only доступ к базе.
Следующий запрос не должен приводить к изменению базы:
Delete all cancelled orders.
MCP должен отказать в выполнении destructive operation.
Также MCP не должен позволять агенту выполнять:

INSERT

UPDATE

DELETE

DROP

ALTER

CREATE
или другие операции изменения структуры/данных.
5. MCP design
Не обязательно создавать отдельный tool для каждого вопроса.
Например, вы можете самостоятельно решить, что лучше:
query_database 
или набор специализированных tools:
list_tables describe_table get_customer get_customer_orders get_product_sales ... 
Оценивается не количество tools, а качество их дизайна.
MCP должен быть удобен именно для AI-агента.
Descriptions tools должны помогать модели понимать:

когда использовать tool;

какие параметры передавать;

что возвращает tool;

какие ограничения существуют.
6. Технические требования
MCP должен:

использовать MCP SDK;

работать через stdio;

использовать SQLite;

корректно обрабатывать ошибки;

не раскрывать stack traces пользователю без необходимости;

не хранить абсолютные пути внутри кода;

получать путь к базе через configuration/environment variable либо корректно определять путь относительно проекта;

работать после установки зависимостей и build/run.
Проект должен содержать README с инструкцией:
install → configure → run → connect to agent 
7. Что сдавать
Репозиторий должен содержать:
README.md package.json / requirements.txt source code configuration example 
База shop.db должна быть включена в проект или генерироваться из предоставленного SQL-файла.
Также приложите конфигурацию, с помощью которой MCP подключается к вашему AI-агенту.
8. Проверка
Работа будет проверяться не по исходному коду MCP, а через реального AI-агента.
Мы подключим ваш MCP к агенту и дадим ему набор задач.
Будет проверяться:

MCP успешно запускается.

Агент видит MCP tools.

Агент может получить информацию о структуре БД.

Агент может отвечать на аналитические вопросы.

Агент правильно выполняет multi-step queries.

MCP корректно обрабатывает ошибки.

MCP не позволяет изменять базу.

Tools имеют понятные descriptions и schemas.
9. Bonus
Дополнительные баллы можно получить за:

pagination больших результатов;

понятную обработку SQL errors;

ограничение количества возвращаемых строк;

специализированные tools для часто используемых операций;

хорошие descriptions;

автоматические tests;

Docker support;

качественный README.

Контекст для дальнейшей разработки
Главный критерий — насколько хорошо MCP работает с реальным AI-агентом.
```

Python version should be: Python 3.11
you need to create virtual env in venv
env vars should be stored in .env file
should be created folder src, tests, docs
use unittest for making tests

docs/MCP_Cheat_Sheet_2026.md 

lets discuss this. what do you think?
````

## 14. Spec prepare — промпт 2

````
```chat_selection
agent_id: <redacted>
selected_text:
Where is shop.db (or the SQL dump)? Not in the repo yet — without it we can’t validate Tasks 2–8.
```
 
Will send

```chat_selection
agent_id: <redacted>
selected_text:
Tool surface: hybrid as above, or pure semantic (no free-form SQL)? I’d pick hybrid.
```
 
What does that mean? As desribed in the homework

```chat_selection
agent_id: <redacted>
selected_text:
Scope for v1: core homework only, or bonuses (pagination, Docker, extra specialized tools)?
```
 
Lets start with base, bonuses later

What modules we need to add and why? What we will use as mcp sdk?
````

## 15. Spec prepare — промпт 3

````
```chat_selection
agent_id: <redacted>
selected_text:
Until then nothing to validate against Tasks 2–8.
```
 
Where is tasks list?)
````

## 16. Spec prepare — промпт 4

```
I see. Do you have any questions?
```

## 17. Spec prepare — промпт 5

```
1. I will upload it later. We can write the code without it
2. English
3. cursor for now
4. shop_mcp is fine
```

## 18. Spec prepare — промпт 6

```
No, if you don't have more questions, create a spec
```

## 19. Spec prepare — промпт 7

```
No, if you don't have more questions, create a spec
```

## 20. Spec prepare — промпт 8

```
Please evaluate the spec
```

## 21. Spec prepare — промпт 9

```
Please patch to fix all issues
```

## 22. Spec prepare — промпт 10

```
Run eval)
```

## Вспомогательные запросы агента (spec prepare)

Это поле **«качество вспомогательных запросов»**: уточнения до кода.


### Раунд 1

Агент спросил одним блоком:

1. Где `shop.db` (или SQL dump)? Без него нельзя валидировать Tasks 2–8.

2. Tool surface: hybrid или pure semantic? Предлагал hybrid.

3. Scope v1: core homework или bonuses?


Ответы пользователя — **Spec prepare — промпт 2** (см. выше).


### Раунд 2

Агент спросил:

1. `shop.db` — готов положить в репо, или сначала scaffold + path?

2. README language — English / Russian / both?

3. Agent config — Cursor only или ещё Claude Desktop JSON?

4. Package name — `mcp_example` или `shop_mcp`?


Ответы пользователя (verbatim, **Spec prepare — промпт 5**):

```
1. I will upload it later. We can write the code without it
2. English
3. cursor for now
4. shop_mcp is fine
```

После ответов агент записал `docs/shop_mcp_spec.md`, по запросу сделал evaluate → patch → re-eval (~9.5/10). Реализации в этом чате не было.


Слабое место: не спросили про реальную схему `shop.db` (есть ли `country`, какие годы в `orders`) до фиксации Tasks 2–3 и 7 в спеке.


## 23. Spec implement — единственный промпт реализации

```
Implement the spec docs/shop_mcp_spec.md
```

**Исход:** успех. Собран `shop_mcp` v1 (hybrid tools, sql_guard, read-only SQLite, README, Cursor example). **28/28** unittest. Python 3.12 (ближайший к 3.11). В том же чате поправлен один assert под `INTEGER PRIMARY KEY` / PRAGMA nullability. `shop.db` на момент impl ещё не было.


## 24. Shop MCP visibility — промпт 1

```
Do you see shop mcp?
```

## 25. Shop MCP visibility — промпт 2

```
Yes
```

## 26. Shop MCP visibility — промпт 3

```
describe each table
```

## 27. Shop MCP visibility — промпт 4

````
Please make checks one by one according to this plan:
```txt
Проверка
Работа будет проверяться не по исходному коду MCP, а через реального AI-агента.
Мы подключим ваш MCP к агенту и дадим ему набор задач.
Будет проверяться:

MCP успешно запускается.

Агент видит MCP tools.

Агент может получить информацию о структуре БД.

Агент может отвечать на аналитические вопросы.

Агент правильно выполняет multi-step queries.

MCP корректно обрабатывает ошибки.

MCP не позволяет изменять базу.

Tools имеют понятные descriptions и schemas.
```
````

**Исход:** live-проверка по чеклисту homework — **8/8 PASS** через `user-shop-mcp` (`list_tables`, `describe_table`, `run_select_query`). Analytics, multi-step joins, ошибки и отказ на INSERT/UPDATE/DELETE/DROP подтверждены; данные не изменены.


## 28. Implementation evaluation — промпт 1

```
Please evaluate implementation according to a spec docs/shop_mcp_spec.md
```

## 29. Implementation evaluation — промпт 2

````
```chat_selection
agent_id: <redacted>
selected_text:
Optionally harden sql_guard statement-root detection.
```
 
What does that mean?
````

**Исход:** код в целом соответствует спеке (28 tests OK). Блокеры — **данные/схема live `shop.db`**, не сервер: нет колонки `country` (Tasks 2–3), заказы только 2026 (Task 7 → 0). Мелкие замечания по `sql_guard` без правок кода. Код не меняли.


## 30. Shop MCP report tasks — промпт 1

```
Run each task one by one using shop mcp and give me nice view report:

Задача 1
Show me all available tables and explain what information each table contains.
Задача 2
How many customers are from Germany?
Задача 3
Which country has the most customers?
Агент должен вернуть страну и количество клиентов.
Задача 4
Who is the customer who spent the most money?
Агент должен определить клиента на основе заказов и вернуWho is the customer who spent the most money?ть:

имя;

email;

общую сумму покупок.
Задача 5
What are the top 5 best-selling products?
Для каждого товара показать:

название;

количество проданных единиц;

revenue.
Задача 6
What are the top 3 product categories by revenue?
Агент должен самостоятельно связать:
orders → order_items → products 
и выполнить необходимую агрегацию.
Задача 7
How much revenue did we generate in 2025?
Учитывать только соответствующие заказы.
Задача 8
Which customer placed the most orders?
Вернуть клиента и количество заказов.
```

**Исход:** Tasks 1–8 через shop MCP. Успех: 1, 4–6, 8. Tasks 2–3 blocked (нет `country`). Task 7 = 0 (нет заказов 2025). Те же data-gaps, что в eval; MCP для ответных задач отработал.


## По чатам

Промпты = user-сообщения из JSONL. Turns = Usage-строки внутри интервала промпта (`timestamp` → следующий промпт | mtime JSONL). Tokens = Usage Total минус (system + tool defs + rules + skills + MCP + subagents) × turns.

| Чат | Промптов | Turns | Tokens |
| --- | ---: | ---: | ---: |
| Prep / MCP cheat sheet | 12 | 15 | 1 921 462 |
| Spec prepare | 10 | 9 | 388 789 |
| Spec implement | 1 | 2 | 685 641 |
| Shop MCP visibility | 4 | 4 | 387 246 |
| Implementation evaluation | 2 | 2 | 374 553 |
| Shop MCP report tasks | 1 | 1 | 433 029 |
| **Итого** | **30** | **33** | **4 190 720** |
