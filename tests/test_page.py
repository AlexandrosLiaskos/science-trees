"""Checks of the page: its embedded trees, its scripts and the files that it needs."""

from __future__ import annotations

import base64
import gzip
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "site" / "index.html"


class Scripts(HTMLParser):
    """Collects the script elements of the page with their type and content."""

    def __init__(self) -> None:
        super().__init__()
        self.scripts: list[tuple[dict[str, str | None], str]] = []
        self._current: dict[str, str | None] | None = None
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            self._current = dict(attrs)
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._current is not None:
            self.scripts.append((self._current, "".join(self._parts)))
            self._current = None


def count_nodes(nodes: list[dict]) -> int:
    return sum(1 + count_nodes(node.get("k", [])) for node in nodes)


class PageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PAGE.read_text(encoding="utf-8")
        parser = Scripts()
        parser.feed(cls.text)
        cls.scripts = parser.scripts

    def test_title(self) -> None:
        self.assertIn("<title>The trees of science</title>", self.text)

    def test_embedded_trees(self) -> None:
        blocks = [content for attrs, content in self.scripts if attrs.get("id") == "data"]
        self.assertEqual(len(blocks), 1)
        trees = json.loads(gzip.decompress(base64.b64decode(blocks[0].strip())))
        keys = re.findall(r'\{ key: "([a-z]+)", tab:', self.text)
        self.assertEqual(sorted(trees), sorted(keys), "every tab of the page has a tree")
        for key, nodes in trees.items():
            self.assertGreater(count_nodes(nodes), 0, key)
            stack = list(nodes)
            while stack:
                node = stack.pop()
                self.assertIsInstance(node.get("n"), str)
                self.assertTrue(node["n"].strip(), f"node without a name in {key}")
                stack.extend(node.get("k", []))

    def test_scripts_parse(self) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not installed")
        programs = [content for attrs, content in self.scripts if "type" not in attrs and content.strip()]
        self.assertGreater(len(programs), 0)
        with tempfile.TemporaryDirectory() as folder:
            for index, program in enumerate(programs):
                path = Path(folder) / f"script-{index}.js"
                path.write_text(program, encoding="utf-8")
                result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_no_local_files_needed(self) -> None:
        for reference in re.findall(r'\b(?:src|href)="([^"]+)"', self.text):
            self.assertTrue(
                reference.startswith(("http://", "https://", "data:", "#", "mailto:")),
                f"the page refers to a file that the repository does not hold: {reference}",
            )


if __name__ == "__main__":
    unittest.main()
