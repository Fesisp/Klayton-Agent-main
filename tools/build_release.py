"""
Build Release Tool - Empacotador de Distribuição do Klayton 2.0
================================================================

Gera o pacote limpo de release em dist/Klayton-Agent-2.0.0.zip e suas somas de verificação SHA256.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sys
import hashlib
import zipfile
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def build_release() -> bool:
    print("====================================================")
    print("📦 KLAYTON RELEASE BUILDER")
    print("====================================================")

    dist_dir = ROOT_DIR / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    zip_path = dist_dir / "Klayton-Agent-2.0.0.zip"
    hash_path = dist_dir / "SHA256SUMS.txt"

    print(f"  📁 Gerando pacote limpo em {zip_path.relative_to(ROOT_DIR)}...")

    include_dirs = ["src", "data", "config", "tools", "docs", "tests"]
    include_files = ["RELEASE_MANIFEST.json", "requirements-lock.txt", "README.md", "CHANGELOG.md", "KNOWN_LIMITATIONS.md"]

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for fname in include_files:
            fpath = ROOT_DIR / fname
            if fpath.exists():
                zipf.write(fpath, arcname=fname)

        for dname in include_dirs:
            dpath = ROOT_DIR / dname
            if dpath.exists():
                for fpath in dpath.rglob("*"):
                    if fpath.is_file():
                        # Exclui arquivos temporários e caches
                        if "__pycache__" in str(fpath) or ".pytest_cache" in str(fpath) or fpath.name.endswith(".pyc"):
                            continue
                        rel_p = fpath.relative_to(ROOT_DIR)
                        zipf.write(fpath, arcname=str(rel_p))

    # Calcula hash SHA256
    sha256 = hashlib.sha256()
    with open(zip_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)

    hash_val = sha256.hexdigest()
    hash_path.write_text(f"{hash_val}  Klayton-Agent-2.0.0.zip\n", encoding="utf-8")

    print(f"  ✅ Pacote gerado com sucesso!")
    print(f"  🔐 SHA256: {hash_val}")

    print("====================================================")
    print("STATUS: RELEASE BUILD COMPLETE (READY)")
    print("====================================================")
    return True


if __name__ == "__main__":
    success = build_release()
    sys.exit(0 if success else 1)
