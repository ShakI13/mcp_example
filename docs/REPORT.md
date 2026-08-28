# Отчёт по реализации — Shop MCP Server

Эксперимент: MCP cheat sheet → спека в отдельном чате → реализация в новом чате → live visibility / eval / homework tasks. Отчётный чат в промпты и токены не входит. Чат aborted-impl (Aug 26) не учитывается.

---

## Метрики

| Поле | Значение |
| --- | --- |
| Размер спецификации | **3 924 токен** (`tiktoken o200k_base`). Файл не менялся после impl. |
| Запустился ли с первого раза | **Да** (unittest **28/28** в чате impl; live MCP checklist **8/8**). Homework Tasks 2–3 и 7 упираются в схему/данные `shop.db`, не в падение сервера. |
| Качество вспомогательных запросов | **Среднее+.** Два раунда уточнений до спеки (3 + 4 вопроса). Закрыты DB path, hybrid vs semantic, scope, README/lang, Cursor config, package name. Слабое место: не спросили про реальные колонки/`country`/годы заказов — Tasks 2–3 и 7 потом упёрлись в live DB. |
| Общее количество промптов | **30** user-сообщений (cheat 12 + spec 10 + impl 1 + visibility 4 + eval 2 + tasks 1). После готовой спеки: **8**. |
| Итоговое количество багов | **0** (отдельных bug-fix чатов не было; код после impl не правили). Обнаружены **2 data/schema gap** в live `shop.db` (нет `country`; нет заказов 2025) — это не баги сервера. |
| Общее количество потраченных токенов | **4 190 720** (без system / tool defs / rules / skills / MCP / subagents; **33** model-turn’а) |

---

## Артефакты

| Требование | Где |
| --- | --- |
| Скриншот / лог терминала | `docs/run_log.txt` — **отсутствует** (в репозитории нет) |
| Файл спецификации | `docs/shop_mcp_spec.md` |
| Файл с дополнительными промптами | `docs/extra_prompts.md` |
| Файл с подсчетами | этот файл |

---

## Размер спецификации

Файл: `docs/shop_mcp_spec.md`. На момент impl и сейчас — один и тот же текст (после impl файл не патчили).


| Оценка | Значение |
| --- | --- |
| Символы | 15 192 |
| Слова | 2 247 |
| Строки | 443 |
| `tiktoken o200k_base` | **3 924** |
| `tiktoken cl100k_base` | 3 908 |

---

## Запустился ли с первого раза

**Да** для сервера и тестов.


1. Чат реализации: один user-промпт → код + unittest → **28/28** (в процессе один assert подстроен под SQLite `INTEGER PRIMARY KEY` / PRAGMA `notnull`).
2. Visibility: агент видит MCP tools; checklist homework **8/8 PASS**.
3. Eval / report-tasks: Tasks 2–3 и 7 не отвечаются из‑за live DB (нет `country`, заказы только 2026) — MCP при этом работает на Tasks 1, 4–6, 8.


---

## Качество вспомогательных запросов

Насколько хорошо агент уточнил задачу **до** реализации (не качество кода).


В spec-prepare два раунда вопросов, затем спека. Тексты: `docs/extra_prompts.md`.


| Тема | Спросили? |
| --- | --- |
| Наличие / путь `shop.db` | да |
| Hybrid vs pure semantic tools | да (пользователь сначала не понял «hybrid») |
| Scope v1 / bonuses | да |
| README language | да |
| Cursor vs другие agent configs | да |
| Package / module name | да |
| Реальная схема: колонка country | **нет** |
| Годы заказов (2025 vs 2026) | **нет** |

Оценка: **среднее+**. Решения по tooling/layout закрыты; главный спотык homework (Germany/country, revenue 2025) в Q&A не попал, потому что DB ещё не было.


---

## Баги

Отдельных bug-fix чатов не было — **0**.


| # | Где | Симптом | Статус |
| --- | --- | --- | --- |
| — | live `shop.db` | нет `country` → Tasks 2–3 | data gap, код не меняли |
| — | live `shop.db` | заказы только 2026 → Task 7 = 0 | data gap, код не меняли |

---

## По чатам

Промпты = user-сообщения из JSONL. Turns = строки Cursor Usage, попавшие в интервал `[timestamp промпта → следующий промпт | mtime JSONL]` того же чата. Tokens = Usage Total минус на каждый turn: system + tool defs + rules + skills + MCP + subagents. Строки Usage вне этих интервалов (другие проекты / abort / report) не входят. Тексты: `docs/extra_prompts.md`.

| Чат | Промптов | Turns | Tokens |
| --- | ---: | ---: | ---: |
| Prep / MCP cheat sheet | 12 | 15 | 1 921 462 |
| Spec prepare | 10 | 9 | 388 789 |
| Spec implement | 1 | 2 | 685 641 |
| Shop MCP visibility | 4 | 4 | 387 246 |
| Implementation evaluation | 2 | 2 | 374 553 |
| Shop MCP report tasks | 1 | 1 | 433 029 |
| **Итого** | **30** | **33** | **4 190 720** |
