import os
import unittest

from functions import get_files_info, get_file_content, run_python_file, write_file


class TestFilesInfo(unittest.TestCase):
    def test_calculator_dir(self):
        res = list(get_files_info._get_files_info("calculator", "."))

        self.assertEqual(len(res), 4)
        for item in res:
            if item["name"] == "main.py":
                self.assertFalse(item["is_directory"])
                self.assertGreater(item["size"], 0)
            elif item["name"] == "pkg":
                self.assertTrue(item["is_directory"])
                self.assertGreater(item["size"], 0)
            elif item["name"] == "tests.py":
                self.assertFalse(item["is_directory"])
                self.assertGreater(item["size"], 0)

    def test_invalid_directory(self):
        with self.assertRaises(FileNotFoundError):
            list(get_files_info._get_files_info("calculator", "non_existent_dir"))

    def test_outside_working_directory(self):
        with self.assertRaises(ValueError):
            list(get_files_info._get_files_info("calculator", "../"))

    def test_manual(self):
        print(get_files_info.get_files_info("calculator", "."))
        print(get_files_info.get_files_info("calculator", "pkg"))
        print(get_files_info.get_files_info("calculator", "/bin"))
        print(get_files_info.get_files_info("calculator", "../"))
        self.assertEqual(get_files_info.get_schema().name, "get_files_info")


class TestFilesContent(unittest.TestCase):
    def test_read_calculator_main(self):
        content, truncated = get_file_content._get_file_content("calculator", "main.py")
        self.assertIn("def main():", content)

    def test_invalid_file_path(self):
        with self.assertRaises(FileNotFoundError):
            _ = get_file_content._get_file_content("calculator", "non_existent_file.py")

    def test_file_outside_working_directory(self):
        with self.assertRaises(ValueError):
            _ = get_file_content._get_file_content("calculator", "../some_file.py")

    def test_read_large_file(self):
        content, truncated = get_file_content._get_file_content(
            "calculator", "lorem.txt", max_chars=10000
        )
        self.assertLessEqual(len(content), 10000)

    def test_manual(self):
        print(get_file_content.get_file_content("calculator", "main.py"))
        print(get_file_content.get_file_content("calculator", "pkg/calculator.py"))
        print(get_file_content.get_file_content("calculator", "/bin/cat"))
        print(get_file_content.get_file_content("calculator", "pkg/does_not_exist.py"))
        self.assertEqual(get_file_content.get_schema().name, "get_file_content")


class TestRunPythonFile(unittest.TestCase):
    def test_run_valid_python_file(self):
        stdout, stderr = run_python_file._run_python_file(
            "calculator", "main.py", ["2 + 3 * 4"]
        )
        self.assertIn('"result": 14', stdout)
        self.assertEqual(stderr, "")

    def test_run_python_file_with_error(self):
        stdout, stderr = run_python_file._run_python_file(
            "calculator", "main.py", ["2 / 0"]
        )
        self.assertIn("Error: float division by zero", stdout)
        self.assertEqual(stderr, "")

    def test_run_non_existent_file(self):
        with self.assertRaises(FileNotFoundError):
            _ = run_python_file._run_python_file(
                "calculator", "pkg/non_existent.py", ["2 + 2"]
            )

    def test_run_file_outside_working_directory(self):
        with self.assertRaises(ValueError):
            _ = run_python_file._run_python_file(
                "calculator", "../some_file.py", ["2 + 2"]
            )

    def test_run_non_python_file(self):
        with self.assertRaises(ValueError):
            _ = run_python_file._run_python_file("calculator", "lorem.txt", ["2 + 2"])

    def test_manual(self):
        print(run_python_file.run_python_file("calculator", "main.py"))
        print(run_python_file.run_python_file("calculator", "main.py", ["3 + 5"]))
        print(run_python_file.run_python_file("calculator", "tests.py"))
        print(run_python_file.run_python_file("calculator", "../main.py"))
        print(run_python_file.run_python_file("calculator", "nonexistent.py"))
        print(run_python_file.run_python_file("calculator", "lorem.txt"))
        self.assertEqual(run_python_file.get_schema().name, "run_python_file")


class TestWriteReadFile(unittest.TestCase):
    def test_write_file_within_working_directory(self):
        write_file._write_file("calculator", "test_output.txt", "Hello, World!")

        content, truncated = get_file_content._get_file_content(
            "calculator", "test_output.txt"
        )
        self.assertEqual(content, "Hello, World!")
        self.assertFalse(truncated)
        os.remove("calculator/test_output.txt")

    def test_write_file_outside_working_directory(self):
        with self.assertRaises(ValueError):
            write_file._write_file("calculator", "../outside.txt", "This should fail")

    def test_write_file_in_subdirectory(self):
        self.assertFalse(os.path.exists("calculator/subdir"))
        write_file._write_file(
            "calculator", "subdir/test_subdir_output.txt", "Subdirectory Test"
        )

        content, truncated = get_file_content._get_file_content(
            "calculator", "subdir/test_subdir_output.txt"
        )
        self.assertEqual(content, "Subdirectory Test")
        self.assertFalse(truncated)
        os.remove("calculator/subdir/test_subdir_output.txt")
        os.rmdir("calculator/subdir")

    def test_write_large_content(self):
        large_content = "A" * 15000
        write_file._write_file("calculator", "large_output.txt", large_content)

        content, truncated = get_file_content._get_file_content(
            "calculator", "large_output.txt", max_chars=10
        )
        self.assertEqual(content, "A" * 10)
        self.assertTrue(truncated)
        os.remove("calculator/large_output.txt")

    def test_manual(self):
        # print(write_file.write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"))
        print(
            write_file.write_file(
                "calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"
            )
        )
        print(
            write_file.write_file(
                "calculator", "/tmp/temp.txt", "this should not be allowed"
            )
        )
        self.assertEqual(write_file.get_schema().name, "write_file")


if __name__ == "__main__":
    # manual test
    for t in [
        TestFilesInfo(),
        TestFilesContent(),
        TestWriteReadFile(),
        TestRunPythonFile(),
    ]:
        t.test_manual()

    # proper tests
    unittest.main()
