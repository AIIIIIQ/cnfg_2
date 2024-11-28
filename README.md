# Dependency Graph Visualizer

## 1. Общее описание

**Dependency Graph Visualizer** — это инструмент командной строки для генерации графов зависимостей npm-пакетов. Он использует Mermaid для визуализации зависимостей, включая транзитивные и циклические зависимости, и сохраняет результат в формате PNG.

Основные возможности:
- Автоматическое извлечение зависимостей с помощью npm.
- Генерация графа зависимостей в формате Mermaid.
- Сохранение графа в формате PNG.
- Настройка глубины анализа зависимостей.

---

## 2. Описание всех функций и настроек

### Основные функции (из `graph_generator.py`):
- **`get_dependencies(package_name, max_depth)`**:
  Рекурсивно извлекает зависимости указанного npm-пакета с заданной глубиной. Возвращает граф зависимостей в виде словаря.

- **`generate_mermaid(graph)`**:
  Конвертирует граф зависимостей (словарь) в Mermaid-схему.

- **`save_mermaid_as_png(mermaid_code, output_file, graphviz_path)`**:
  Сохраняет Mermaid-схему в виде PNG-файла. Для этого используется `mmdc` (Mermaid CLI).

- **`main()`**:
  Точка входа для командной строки. Парсит аргументы и запускает процесс извлечения зависимостей, генерации Mermaid-кода и сохранения в PNG.

### Настройки командной строки:
- `--graphviz-path`: Путь к программе `mmdc` для визуализации графов.
- `--package-name`: Имя анализируемого npm-пакета.
- `--output-file`: Путь для сохранения итогового PNG-файла.
- `--max-depth`: Максимальная глубина анализа зависимостей.

Пример команды:
```bash
python graph_generator.py --graphviz-path "C:\Users\user\AppData\Roaming\npm\mmdc.cmd" \
    --package-name "express" --output-file "express_graph.png" --max-depth 1
```

---

## 3. Описание команд для сборки проекта

Необходимы установленые Node.js и `@mermaid-js/mermaid-cli`

### Запуск основного скрипта:
```bash
python graph_generator.py --graphviz-path "путь_к_mmdc" \
    --package-name "имя_пакета" --output-file "имя_файла.png" --max-depth глубина
```

### Запуск тестов:
Для запуска тестов выполните:
```bash
python -m unittest test_graph_generator.py
```

---

## 4. Результаты прогона тестов

Запуск тестов:
```bash
python -m unittest test_graph_generator.py
```

Результат:


https://github.com/user-attachments/assets/84e5ebad-a1f5-489a-9004-d3dd2023c82e


