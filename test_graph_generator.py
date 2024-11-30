import unittest
from unittest.mock import patch, MagicMock
import os
import json
import subprocess
from graph_generator import get_dependencies, generate_mermaid, save_mermaid_as_png


class TestDependencyGraph(unittest.TestCase):
    @patch("requests.get")
    def test_get_dependencies_single_level(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            'dist-tags': {'latest': '1.0.0'},
            'versions': {
                '1.0.0': {
                    'dependencies': {'dep1': '1.0.0', 'dep2': '2.0.0'}
                }
            }
        }
        mock_get.return_value = mock_response

        result = get_dependencies("test_package", max_depth=1)
        expected_result = {"test_package": ["dep1", "dep2"]}
        self.assertEqual(result, expected_result)

    @patch("requests.get")
    def test_get_dependencies_transitive(self, mock_get):
        # Словарь, чтобы возвращать разные ответы на разные запросы
        responses = {
            'test_package': {
                'dist-tags': {'latest': '1.0.0'},
                'versions': {
                    '1.0.0': {
                        'dependencies': {'dep1': '1.0.0'}
                    }
                }
            },
            'dep1': {
                'dist-tags': {'latest': '1.0.0'},
                'versions': {
                    '1.0.0': {
                        'dependencies': {'dep2': '2.0.0'}
                    }
                }
            },
            'dep2': {
                'dist-tags': {'latest': '2.0.0'},
                'versions': {
                    '2.0.0': {
                        'dependencies': {}
                    }
                }
            }
        }

        def side_effect(url, *args, **kwargs):
            package_name = url.split('/')[-1]
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = responses.get(package_name, {})
            return mock_response

        mock_get.side_effect = side_effect

        result = get_dependencies("test_package", max_depth=2)
        expected_result = {
            "test_package": ["dep1"],
            "dep1": ["dep2"]
        }
        self.assertEqual(result, expected_result)

    @patch("requests.get")
    def test_get_dependencies_no_dependencies(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            'dist-tags': {'latest': '1.0.0'},
            'versions': {
                '1.0.0': {
                    'dependencies': {}
                }
            }
        }
        mock_get.return_value = mock_response

        result = get_dependencies("test_package", max_depth=1)
        expected_result = {"test_package": []}
        self.assertEqual(result, expected_result)

    def test_generate_mermaid(self):
        graph = {
            "packageA": ["packageB", "packageC"],
            "packageB": ["packageD"],
            "packageC": [],
            "packageD": []
        }
        expected_mermaid = """graph TD
    packageA --> packageB
    packageA --> packageC
    packageB --> packageD"""
        result = generate_mermaid(graph)
        self.assertEqual(result.strip(), expected_mermaid.strip())

    @patch("subprocess.run")
    def test_save_mermaid_as_png(self, mock_subprocess_run):
        mermaid_code = "graph TD\n    packageA --> packageB"
        output_file = "test_graph2.png"
        graphviz_path = "C:\\Users\\a0908\\AppData\\Roaming\\npm\\mmdc.cmd"

        mock_subprocess_run.return_value = MagicMock(returncode=0)

        save_mermaid_as_png(mermaid_code, output_file, graphviz_path)

        self.assertTrue(os.path.exists(output_file.replace(".png", ".mmd")), f"{output_file.replace('.png', '.mmd')} не был создан")
        # Не проверяем наличие PNG-файла, так как мы замокали subprocess.run

        os.remove(output_file.replace(".png", ".mmd"))

    @patch("requests.get")
    @patch("subprocess.run")
    def test_full_flow(self, mock_subprocess_run, mock_get):
        mock_subprocess_run.return_value = MagicMock(returncode=0)

        # Мокаем ответ для пакета test_package
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            'dist-tags': {'latest': '1.0.0'},
            'versions': {
                '1.0.0': {
                    'dependencies': {'dep1': '1.0.0', 'dep2': '2.0.0'}
                }
            }
        }
        mock_get.return_value = mock_response

        package_name = "test_package"
        max_depth = 1
        output_file = "test_graph1.png"
        graphviz_path = "C:\\Users\\a0908\\AppData\\Roaming\\npm\\mmdc.cmd"

        dependency_graph = get_dependencies(package_name, max_depth)
        mermaid_code = generate_mermaid(dependency_graph)

        save_mermaid_as_png(mermaid_code, output_file, graphviz_path)

        mermaid_file = output_file.replace(".png", ".mmd")
        self.assertTrue(os.path.exists(mermaid_file), f"{mermaid_file} не был создан")
        print(f"Mermaid файл создан: {mermaid_file}")

        os.remove(mermaid_file)

    @patch("requests.get")
    @patch("subprocess.run")
    def test_file_based_dependencies(self, mock_subprocess_run, mock_get):
        mock_subprocess_run.return_value = MagicMock(returncode=0)

        # Пути к JSON-файлам зависимостей
        files = ["dependencies_1.json", "dependencies_2.json", "dependencies_3.json"]

        output_files = [
            "test_graph_dependencies_1.png",
            "test_graph_dependencies_2.png",
            "test_graph_dependencies_3.png",
        ]

        graphviz_path = "C:\\Users\\a0908\\AppData\\Roaming\\npm\\mmdc.cmd"

        for i, file in enumerate(files):
            with open(file, "r") as f:
                dependencies = json.load(f)

            # Мокаем ответ requests.get
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = {
                'dist-tags': {'latest': '1.0.0'},
                'versions': {
                    '1.0.0': {
                        'dependencies': dependencies.get('dependencies', {})
                    }
                }
            }
            mock_get.return_value = mock_response

            # Получаем имя пакета из файла
            package_name = dependencies.get('name', f'package_{i}')

            # Генерируем граф зависимостей
            dependency_graph = get_dependencies(package_name, max_depth=3)

            mermaid_code = generate_mermaid(dependency_graph)

            # Сохранение в PNG
            output_file = output_files[i]
            save_mermaid_as_png(mermaid_code, output_file, graphviz_path)

            # Проверка, что файлы были созданы
            mermaid_file = output_file.replace(".png", ".mmd")
            self.assertTrue(os.path.exists(mermaid_file), f"{mermaid_file} не был создан")
            # Не проверяем наличие PNG-файла, так как мы замокали subprocess.run

            print(f"Mermaid файл создан: {mermaid_file}")

            os.remove(mermaid_file)


if __name__ == "__main__":
    unittest.main()
