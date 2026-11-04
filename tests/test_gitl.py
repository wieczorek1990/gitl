import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Mock gnureadline before importing gitl.
if sys.platform == "darwin":
    mock_readline = MagicMock()
    sys.modules["gnureadline"] = mock_readline
    sys.modules["readline"] = mock_readline
else:
    sys.modules["readline"] = MagicMock()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import gitl


class TestValidCompletions(unittest.TestCase):
    def test_returns_matching_entries(self):
        entries = ["feature-a", "feature-b", "main", "develop"]
        result = gitl.valid_completions(entries, "feat")
        self.assertEqual(result, ["feature-a", "feature-b"])

    def test_returns_empty_when_no_match(self):
        entries = ["main", "develop"]
        result = gitl.valid_completions(entries, "feat")
        self.assertEqual(result, [])

    def test_empty_input(self):
        result = gitl.valid_completions([], "text")
        self.assertEqual(result, [])

    def test_exact_match(self):
        entries = ["main", "master"]
        result = gitl.valid_completions(entries, "main")
        self.assertEqual(result, ["main"])


class TestSplit(unittest.TestCase):
    def test_splits_on_two_dots(self):
        result = gitl.split("main..feature")
        self.assertEqual(result, ("main", "feature"))

    def test_returns_none_when_no_dots(self):
        result = gitl.split("main")
        self.assertIsNone(result)

    def test_single_dot_returns_none(self):
        result = gitl.split("main.feature")
        self.assertIsNone(result)

    def test_two_dots_at_start(self):
        result = gitl.split("..feature")
        self.assertEqual(result, ("", "feature"))

    def test_two_dots_at_end(self):
        result = gitl.split("main..")
        self.assertEqual(result, ("main", ""))

    def test_multiple_two_dots(self):
        # Should split on the first occurrence.
        result = gitl.split("a..b..c")
        self.assertEqual(result, ("a", "b..c"))


class TestPrefixCompletions(unittest.TestCase):
    def test_adds_prefix_to_completions(self):
        result = gitl.prefix_completions("main..", ["feature", "bugfix"])
        self.assertEqual(result, ["main..feature", "main..bugfix"])

    def test_empty_completions(self):
        result = gitl.prefix_completions("prefix.", [])
        self.assertEqual(result, [])


class TestGetCommands(unittest.TestCase):
    def test_single_command(self):
        result = gitl.GitLoop.get_commands("log")
        self.assertEqual(result, ["log"])

    def test_multiple_commands_with_semicolon(self):
        result = gitl.GitLoop.get_commands("log; status")
        self.assertEqual(result, ["log", "status"])

    def test_semicolon_in_single_quotes(self):
        result = gitl.GitLoop.get_commands("log --grep='a;b'")
        self.assertEqual(result, ["log --grep='a;b'"])

    def test_semicolon_in_double_quotes(self):
        result = gitl.GitLoop.get_commands('log --grep="a;b"')
        self.assertEqual(result, ['log --grep="a;b"'])

    def test_mixed_quotes(self):
        # Semicolon in double quotes should not split.
        result = gitl.GitLoop.get_commands("log; 'a;b'")
        self.assertEqual(result, ["log", "'a;b'"])

    def test_empty_commands(self):
        result = gitl.GitLoop.get_commands("log;; status")
        self.assertEqual(result, ["log", "", "status"])

    def test_whitespace_stripping(self):
        result = gitl.GitLoop.get_commands("  log  ;  status  ")
        self.assertEqual(result, ["log", "status"])

    def test_trailing_semicolon(self):
        result = gitl.GitLoop.get_commands("log;")
        self.assertEqual(result, ["log", ""])

    def test_nested_quotes(self):
        # Single quote inside double quotes should not toggle single quote state.
        result = gitl.GitLoop.get_commands('log --grep="it\'s"; status')
        self.assertEqual(result, ['log --grep="it\'s"', "status"])


class TestAnchor(unittest.TestCase):
    @patch("os.getcwd", return_value="/home/user/myproject")
    def test_anchor_root(self, mock_cwd):
        anchor = gitl.Anchor()
        self.assertEqual(anchor.root, "myproject: ")

    @patch("os.getcwd", return_value="/home/user/myproject")
    def test_anchor_str(self, mock_cwd):
        anchor = gitl.Anchor()
        self.assertEqual(str(anchor), "myproject: ")


class TestPrintVersion(unittest.TestCase):
    @patch("builtins.print")
    def test_prints_version(self, mock_print):
        gitl.print_version()
        mock_print.assert_called_once_with(f"gitl version {gitl.VERSION}")


class TestPrintHelp(unittest.TestCase):
    @patch("builtins.print")
    def test_prints_help(self, mock_print):
        gitl.print_help()
        self.assertTrue(mock_print.called)
        args, _ = mock_print.call_args
        self.assertIn("SYNOPSIS", args[0])
        self.assertIn("--help", args[0])
        self.assertIn("--version", args[0])


class TestExecute(unittest.TestCase):
    def test_prints_error_on_malformed_command(self):
        with patch("builtins.print") as mock_print:
            gitl.GitLoop.execute('log --grep="unfinished')
            mock_print.assert_called_once()
            self.assertIn("malformed command", mock_print.call_args[0][0])

    def test_skips_empty_commands(self):
        with patch.object(gitl.GitLoop, "execute_command") as mock_exec:
            gitl.GitLoop.execute("log; ; status")
            self.assertEqual(mock_exec.call_count, 2)


class TestRun(unittest.TestCase):
    @patch("gitl.subprocess.run")
    def test_run_returns_output(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = b"output"
        mock_run.return_value = mock_result
        result = gitl.run(["git", "status"])
        self.assertEqual(result, "output")

    @patch("gitl.subprocess.run")
    def test_run_returns_none_when_no_stdout(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = None
        mock_run.return_value = mock_result
        result = gitl.run(["git", "status"])
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
