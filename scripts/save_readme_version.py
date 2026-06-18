#!/usr/bin/env python3
"""
save_readme_version.py — README 版本归档工具

每次更新 README 前运行此脚本, 自动保存当前版本到 .reasonix/readme-versions/。

用法:
    python scripts/save_readme_version.py                    # 自动版本号
    python scripts/save_readme_version.py --version v0.3.0   # 指定版本
    python scripts/save_readme_version.py --list              # 列出所有版本
"""

from __future__ import annotations
import shutil
import sys
from datetime import datetime
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
VERSIONS_DIR = ROOT / ".reasonix" / "readme-versions"


def list_versions():
    """列出所有已保存的 README 版本。"""
    versions = sorted(VERSIONS_DIR.glob("README-*.md"))
    if not versions:
        print("未找到已保存的 README 版本。")
        return
    print(f"已保存 {len(versions)} 个 README 版本:\n")
    for v in versions:
        size = v.stat().st_size
        name = v.stem.replace("README-", "", 1)
        print(f"  {name:<50} {size:>6}B")


def get_next_version() -> str:
    """自动计算下一个版本号。"""
    existing = list(VERSIONS_DIR.glob("README-v*.md"))
    if not existing:
        return "v0.1.0"

    versions = []
    for f in existing:
        m = re.search(r"v(\d+)\.(\d+)\.(\d+)", f.name)
        if m:
            versions.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
    if not versions:
        return "v0.1.0"

    latest = max(versions)
    return f"v{latest[0]}.{latest[1]}.{latest[2] + 1}"


def save_version(version: str = ""):
    """保存当前 README 版本。"""
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    if not README.exists():
        print(f"错误: README.md 不存在: {README}")
        return False

    if not version:
        version = get_next_version()

    date_str = datetime.now().strftime("%Y%m%d-%H%M")
    dest = VERSIONS_DIR / f"README-{version}-{date_str}.md"

    shutil.copy2(README, dest)
    print(f"✅ 已保存: {dest.name} ({dest.stat().st_size}B)")
    print(f"   版本 {version} → {dest}")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="README 版本归档工具")
    parser.add_argument("--version", "-v", default="",
                       help="版本号 (默认: 自动递增)")
    parser.add_argument("--list", "-l", action="store_true",
                       help="列出所有已保存版本")
    args = parser.parse_args()

    if args.list:
        list_versions()
        return

    save_version(args.version)


if __name__ == "__main__":
    main()
