import unittest
from unittest.mock import patch, MagicMock
import os
import json
from graph_generator import get_dependencies, generate_mermaid, save_mermaid_as_png


class TestDependencyGraph(unittest.TestCase):
    @patch("subprocess.run")
    def test_get_dependencies_single_level(self, mock_subprocess_run):
        mock_subprocess_run.return_value = MagicMock(stdout='{"dep1": "1.0.0", "dep2": "2.0.0"}')
        result = get_dependencies("test_package", max_depth=1)
        expected_result = {"test_package": ["dep1", "dep2"]}
        self.assertEqual(result, expected_result)

    @patch("subprocess.run")
    def test_get_dependencies_transitive(self, mock_subprocess_run):
        mock_subprocess_run.side_effect = [
            MagicMock(stdout='{"dep1": "1.0.0"}'),
            MagicMock(stdout='{"dep2": "2.0.0"}')
        ]
        result = get_dependencies("test_package", max_depth=2)
        expected_result = {"test_package": ["dep1"], "dep1": ["dep2"]}
        self.assertEqual(result, expected_result)

    @patch("subprocess.run")
    def test_get_dependencies_no_dependencies(self, mock_subprocess_run):
        mock_subprocess_run.return_value = MagicMock(stdout='{}')
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

    def test_save_mermaid_as_png(self):
        mermaid_code = "graph TD\n    packageA --> packageB"
        output_file = "test_graph2.png"
        graphviz_path = "C:\\Users\\a0908\\AppData\\Roaming\\npm\\mmdc.cmd"

        save_mermaid_as_png(mermaid_code, output_file, graphviz_path)

        self.assertTrue(os.path.exists(output_file.replace(".png", ".mmd")), f"{output_file.replace('.png', '.mmd')} не был создан")
        self.assertTrue(os.path.exists(output_file), f"{output_file} не был создан")

        os.remove(output_file.replace(".png", ".mmd"))

    def test_full_flow(self):
        package_name = "test_package"
        max_depth = 1
        output_file = "test_graph1.png"
        graphviz_path = "C:\\Users\\a0908\\AppData\\Roaming\\npm\\mmdc.cmd"

        graph = {"test_package": ["dep1", "dep2"]}
        mermaid_code = generate_mermaid(graph)

        save_mermaid_as_png(mermaid_code, output_file, graphviz_path)

        mermaid_file = output_file.replace(".png", ".mmd")
        self.assertTrue(os.path.exists(mermaid_file), f"{mermaid_file} не был создан")
        print(f"Mermaid файл создан: {mermaid_file}")

        self.assertTrue(os.path.exists(output_file), f"{output_file} не был создан")
        print(f"PNG файл создан: {output_file}")

        os.remove(output_file.replace(".png", ".mmd"))

    def test_file_based_dependencies(self):
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

            # Генерация Mermaid-схемы
            mermaid_code = generate_mermaid(dependencies)

            # Сохранение в PNG
            output_file = output_files[i]
            save_mermaid_as_png(mermaid_code, output_file, graphviz_path)

            # Проверка, что файлы были созданы
            mermaid_file = output_file.replace(".png", ".mmd")
            self.assertTrue(os.path.exists(mermaid_file), f"{mermaid_file} не был создан")
            self.assertTrue(os.path.exists(output_file), f"{output_file} не был создан")

            print(f"Mermaid файл создан: {mermaid_file}")
            print(f"PNG файл создан: {output_file}")

            os.remove(output_file.replace(".png", ".mmd"))


if __name__ == "__main__":
    unittest.main()
