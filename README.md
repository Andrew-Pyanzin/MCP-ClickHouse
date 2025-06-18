# Агент для аналитики данных из ClickHouse

Этот проект представляет собой агента для командной строки, который работает как гибридный аналитик данных. Он может выбирать между выполнением прямых SQL-запросов к базе данных ClickHouse и проведением сложного анализа данных с использованием интегрированной среды Python с библиотеками `pandas` и `numpy`.

Эта двойная возможность позволяет агенту справляться с широким кругом задач, от простого извлечения данных до многоэтапного анализа, который был бы затруднителен или невозможен только с помощью SQL.

## Как это работает: Рабочий процесс с двумя инструментами

Агент работает с двумя основными инструментами и решает, какой из них использовать, в зависимости от вашего вопроса:

1.  **SQL Executor (`execute_clickhouse_query`):** Для вопросов, на которые можно ответить прямым запросом к базе данных (например, "Покажи мне последние 10 событий"), агент использует этот инструмент. Он подключается к постоянному серверу MCP (`server.py`), который обеспечивает безопасное соединение с ClickHouse.
2.  **Python Sandbox (`python`):** Для более сложных вопросов (например, "Каково среднее время сеанса?") агент может писать и выполнять код на Python. Он может использовать `pandas` для манипулирования данными и `numpy` для численного анализа. Важно отметить, что инструмент Python может *вызывать* инструмент SQL, чтобы сначала получить данные, необходимые для анализа.

## Инструкции по установке

### 1. Установливаем зависимости

Этот проект использует `uv` для управления пакетами.

```bash
# Переходим в каталог проекта
cd Prototypes/BuildMCPServer

# Создаём виртуальное окружение и установливаем все зависимости
uv venv
source .venv/bin/activate
uv pip install -e .
```
Это установит `beeai-framework`, `mcp`, `clickhouse-connect`, `pandas` и `numpy`.

### 2. Настраиваем подключение к MCP-серверу

Агент подключается к серверу MCP (`server.py`), используя параметры из файла `mcp_config.json`. Этот файл определяет команду для запуска сервера. Мы можем изменить его, если наша среда требует другой команды.

```json
{
  "connection_type": "stdio",
  "command": "uv",
  "args": [
    "run",
    "server.py"
  ],
  "env": null
}
```

### 3. Настраиваем подключение к ClickHouse

Сервер MCP (`server.py`) подключается к ClickHouse с использованием переменных окружения. Установим их в нашем терминале:

```bash
export CLICKHOUSE_HOST='localhost'
export CLICKHOUSE_PORT='8123'
export CLICKHOUSE_USER='default'
export CLICKHOUSE_PASSWORD=''
```

### 4. Настраиваем подключение к базе данных в IDE (рекомендуется)

Хотя агент может запрашивать базу данных за нас, рекомендуется также иметь прямое подключение из вашей IDE для проверки и исследования. Используем расширение **SQLTools** в VS Code/Cursor

## Как использовать гибридного агента

Новый рабочий процесс требует двух отдельных терминалов: один для сервера MCP и один для агента.

**Терминал 1: Запускаем сервер MCP**

Этот сервер поддерживает постоянное соединение с вашей базой данных.

```bash
# Убедитесь, что ваше виртуальное окружение активно
source .venv/bin/activate

# Запустите сервер
uv run server.py
```
Оставляем этот терминал запущенным.

**Терминал 2: Запускаем агента**

Теперь можем задавать агенту вопросы в отдельном терминале.

```bash
# Убедитесь, что виртуальное окружение активно
source .venv/bin/activate

# Задайте вопрос в кавычках. Агент решит, какой инструмент лучше использовать.
uv run data_analytics_agent.py "Выведи первые 5 событий из базы данных и отобрази их в pandas DataFrame."
```

**Ожидаемый вывод:**

Агент покажет код Python, который он намеревается выполнить, а затем предоставит окончательный, отформатированный вывод из скрипта.

```text
--- Code to be Executed ---
import json
import pandas as pd
sql_result_json = execute_clickhouse_query(query='''SELECT * FROM events LIMIT 5''')
data = json.loads(sql_result_json)
df = pd.DataFrame(data)
print(df)
---------------------------

--- Agent Final Response ---
  event_id                              user_id   event_name   event_timestamp      ...
0 00000000-0000-0000-0000-000000000000  user_123  app_open     2023-01-15 10:00:00  ...
...
--------------------------
```

---
<br>

# Hybrid AI Data Analytics Agent from ClickHouse

This project provides a sophisticated command-line AI agent that functions as a hybrid data analyst. It can intelligently choose between executing direct SQL queries against a ClickHouse database and performing complex data analysis using an integrated Python environment with `pandas` and `numpy`.

This dual capability allows the agent to handle a wide range of tasks, from simple data retrieval to multi-step analysis that would be difficult or impossible with SQL alone.

## How It Works: The Dual-Tool Workflow

The agent operates with two primary tools and decides which one to use based on your question:

1.  **SQL Executor (`execute_clickhouse_query`):** For questions that can be answered with a direct database query (e.g., "Show me the last 10 events"), the agent uses this tool. It connects to a persistent MCP server (`server.py`) that handles the secure connection to ClickHouse.
2.  **Python Sandbox (`python`):** For more complex questions (e.g., "What is the average session time?"), the agent can write and execute Python code. It can use `pandas` for data manipulation and `numpy` for numerical analysis. Crucially, the Python tool can *call* the SQL tool to first fetch the data it needs to analyze.

## Setup Instructions

### 1. Install Dependencies

This project uses `uv` for package management.

```bash
# Navigate to the project directory
cd Prototypes/BuildMCPServer

# Create a virtual environment and install all dependencies
uv venv
source .venv/bin/activate
uv pip install -e .
```
This will install `beeai-framework`, `mcp`, `clickhouse-connect`, `pandas`, and `numpy`.

### 2. Configure MCP Server Connection

The agent connects to the MCP server (`server.py`) using the parameters in the `mcp_config.json` file. This file defines the command to start the server. You can modify it if your environment requires a different command.

```json
{
  "connection_type": "stdio",
  "command": "uv",
  "args": [
    "run",
    "server.py"
  ],
  "env": null
}
```

### 3. Configure ClickHouse Connection

The MCP server (`server.py`) connects to ClickHouse using environment variables. Set them in your terminal:

```bash
export CLICKHOUSE_HOST='localhost'
export CLICKHOUSE_PORT='8123'
export CLICKHOUSE_USER='default'
export CLICKHOUSE_PASSWORD=''
```

### 4. Set Up IDE Database Connection (Recommended)

While the agent can query the database for you, it's best practice to also have a direct connection from your IDE for verification and exploration. Use the **SQLTools** extension in VS Code/Cursor as described in the previous versions of this README.

## How to Use the Hybrid Agent

The new workflow requires two separate terminals: one for the MCP server and one for the agent.

**Terminal 1: Start the MCP Server**

This server maintains the persistent connection to your database.

```bash
# Make sure your virtual environment is active
source .venv/bin/activate

# Run the server
uv run server.py
```
Leave this terminal running.

**Terminal 2: Run the Agent**

Now you can ask the agent questions in a separate terminal.

```bash
# Make sure your virtual environment is active
source .venv/bin/activate

# Ask a question in quotes. The agent will decide the best tool to use.
uv run data_analytics_agent.py "Fetch the first 5 events from the database and display them in a pandas DataFrame."
```

**Expected Output:**

The agent will show the Python code it intends to run and then provide the final, formatted output from the script.

```text
--- Code to be Executed ---
import json
import pandas as pd
sql_result_json = execute_clickhouse_query(query='''SELECT * FROM events LIMIT 5''')
data = json.loads(sql_result_json)
df = pd.DataFrame(data)
print(df)
---------------------------

--- Agent Final Response ---
  event_id                              user_id   event_name   event_timestamp      ...
0 00000000-0000-0000-0000-000000000000  user_123  app_open     2023-01-15 10:00:00  ...
...
--------------------------
``` 
