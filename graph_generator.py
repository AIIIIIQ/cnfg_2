import os
import json
import sys
from argparse import ArgumentParser
import requests
import subprocess

def get_dependencies(package_name, max_depth, current_depth=0, seen=None):
    if seen is None:
        seen = set()

    if package_name in seen or current_depth >= max_depth:
        return {}

    seen.add(package_name)

    try:
        response = requests.get(f'https://registry.npmjs.org/{package_name}')
        response.raise_for_status()
        data = response.json()
        # Получаем информацию о последней версии пакета
        version = data.get('dist-tags', {}).get('latest', '')
        if not version:
            print(f"Не удалось получить информацию о последней версии пакета {package_name}")
            return {}
        dependencies = data.get('versions', {}).get(version, {}).get('dependencies', {})
        if dependencies is None:
            dependencies = {}
    except requests.RequestException as e:
        print(f"Ошибка при получении зависимостей для {package_name}: {e}", file=sys.stderr)
        return {}

    graph = {package_name: list(dependencies.keys())}
    for dep in dependencies:
        graph.update(get_dependencies(dep, max_depth, current_depth + 1, seen))

    return graph


def generate_mermaid(graph):
    lines = ["graph TD"]
    for package, deps in graph.items():
        for dep in deps:
            lines.append(f"    {package} --> {dep}")
    return "\n".join(lines)


def save_mermaid_as_png(mermaid_code, output_file, graphviz_path):
    mermaid_file = output_file.replace(".png", ".mmd")
    with open(mermaid_file, "w") as f:
        f.write(mermaid_code)

    print(f"Mermaid файл создан: {mermaid_file}")

    try:
        print(f"Запуск команды: {graphviz_path} -i {mermaid_file} -o {output_file}")
        subprocess.run(
            [graphviz_path, "-i", mermaid_file, "-o", output_file],
            check=True
        )
        print(f"PNG файл создан: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения команды mmdc: {e}")
        raise


def main():
    parser = ArgumentParser(description="Генератор графов зависимостей для npm-пакетов")
    parser.add_argument("--graphviz-path", required=True, help="Путь к программе для визуализации графов")
    parser.add_argument("--package-name", required=True, help="Имя анализируемого пакета")
    parser.add_argument("--output-file", required=True, help="Путь к файлу для сохранения графа (PNG)")
    parser.add_argument("--max-depth", type=int, default=3, help="Максимальная глубина анализа зависимостей")

    args = parser.parse_args()

    print(f"Получение зависимостей для {args.package_name}...")
    dependency_graph = get_dependencies(args.package_name, args.max_depth)

    if not dependency_graph:
        print("Зависимости не найдены или произошла ошибка.", file=sys.stderr)
        sys.exit(1)

    print("Генерация Mermaid-схемы...")
    mermaid_code = generate_mermaid(dependency_graph)

    print("Сохранение графа зависимостей в PNG...")
    save_mermaid_as_png(mermaid_code, args.output_file, args.graphviz_path)

    print(f"Граф зависимостей успешно сохранен в {args.output_file}.")


if __name__ == "__main__":
    main()
