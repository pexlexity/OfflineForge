# Minimal CLI skeleton (MVP)
import argparse
import json
import hashlib
import os
import tarfile
import tempfile
import subprocess
from pathlib import Path

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def collect_python_wheels(requirements_path, outdir):
    """
    MVP implementation: use pip download to fetch wheels into outdir.
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = ["pip", "download", "-r", str(requirements_path), "-d", str(outdir), "--no-deps"]
    subprocess.check_call(cmd)
    return list(outdir.iterdir())

def collect_npm_packages(package_json_path, outdir):
    """
    MVP: use npm pack for top-level dependencies (simplified).
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    # Very simplified: parse package.json and npm pack each dependency name@version (not resolving transitive deps)
    pkg = json.load(open(package_json_path))
    deps = pkg.get("dependencies", {})
    collected = []
    for name, ver in deps.items():
        print(f"[npm] packing {name}@{ver}")
        # npm pack will create tarball in CWD; run inside outdir
        subprocess.check_call(["npm", "pack", f"{name}@{ver}"], cwd=str(outdir))
        # find resulting tarball
        for f in outdir.iterdir():
            if f.name.startswith(name.replace("/", "-")) and f.suffixes:
                collected.append(f)
    return collected

def build_offline_pack(manifests, out_path):
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        artifacts_dir = tmpdir / "artifacts"
        artifacts_dir.mkdir()
        manifest_out = []
        for m in manifests:
            p = Path(m)
            if not p.exists():
                raise FileNotFoundError(f"Manifest not found: {m}")
            if p.name == "requirements.txt":
                print("[*] Collecting python wheels...")
                wheels = collect_python_wheels(p, artifacts_dir / "pip")
                for w in wheels:
                    manifest_out.append({"type":"wheel","path":str(w.relative_to(tmpdir)),"sha256":sha256_file(w)})
            elif p.name == "package.json":
                print("[*] Collecting npm packages (MVP)...")
                pkgs = collect_npm_packages(p, artifacts_dir / "npm")
                for pkg in pkgs:
                    manifest_out.append({"type":"npm","path":str(pkg.relative_to(tmpdir)),"sha256":sha256_file(pkg)})
            else:
                print(f"Skipping unknown manifest type: {p}")

        # write manifest.json
        manifest_file = tmpdir / "manifest.json"
        manifest_file.write_text(json.dumps(manifest_out, indent=2))

        # write install.sh (simple)
        install_sh = tmpdir / "install.sh"
        install_sh.write_text("#!/usr/bin/env bash\nset -e\n# Простая установка pip wheels\nif [ -d artifacts/pip ]; then\n  pip install --no-index --find-links=artifacts/pip -r requirements.txt\nfi\n# Для npm: распаковать и npm install из локального файла (MVP)\nif [ -d artifacts/npm ]; then\n  echo \"npm packages are stored in artifacts/npm\"\nfi\n")
        install_sh.chmod(0o755)

        # pack to tar.zst (requires zstd)
        out_path = Path(out_path)
        tmp_tar = tmpdir + ".tar"
        with tarfile.open(tmp_tar, "w") as tar:
            tar.add(tmpdir, arcname=".")
        # compress with zstd if available
        try:
            subprocess.check_call(["zstd", "-q", "-19", "-o", str(out_path), tmp_tar])
        except Exception:
            # fallback to tar.gz
            with tarfile.open(str(out_path)+".gz","w:gz") as gz:
                gz.add(tmpdir, arcname=".")
            out_path = Path(str(out_path)+".gz")
        print(f"[+] Offline pack created: {out_path}")
        return out_path

def main():
    parser = argparse.ArgumentParser(prog="offlineforge")
    parser.add_argument("command", choices=["build"], help="Команда")
    parser.add_argument("--manifest", action="append", required=True, help="Путь к манифесту (requirements.txt, package.json)")
    parser.add_argument("--out", required=True, help="Выходной архив (tar.zst)")
    args = parser.parse_args()
    if args.command == "build":
        build_offline_pack(args.manifest, args.out)

if __name__ == "__main__":
    main()
