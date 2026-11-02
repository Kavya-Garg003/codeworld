from .common import ParseResult, Symbol, ImportRec, CallRec, is_test_path
from .python_parser import parse_python
from .js_parser import parse_js

LANG_BY_EXT = {".py": "python", ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
               ".ts": "typescript", ".tsx": "typescript"}


def parse_file(path: str, src: bytes) -> ParseResult:
    ext = "." + path.rsplit(".", 1)[-1].lower() if "." in path else ""
    if ext == ".py":
        return parse_python(path, src)
    return parse_js(path, src)
