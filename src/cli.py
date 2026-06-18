#!/usr/bin/env python3
"""硅基生命体 CLI 入口。在任何目录下均可运行。"""
import sys
from pathlib import Path

# 无论从哪个目录调用, 都定位到项目根
_cli_path = Path(__file__).resolve()
if _cli_path.name == 'cli.py' and _cli_path.parent.name == 'src':
    _root = _cli_path.parent.parent
else:
    _root = Path.cwd()
    for p in [_root] + list(_root.parents):
        if (p / 'AGENTS.md').exists():
            _root = p
            break

if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def main():
    """入口函数 (供 console_scripts 调用)。"""
    from src.main import main as _run
    _run()


if __name__ == "__main__":
    main()
