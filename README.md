# OfflineForge 💾
**OfflineForge** is a universal tool for creating portable offline packages of dependencies and environments
(npm/pip/apt/containers/… ) for development, deployment and recovery of systems without internet access.

---

## What the project does (MVP) 🤷‍♂️
- CLI accepting `package.json` and `requirements.txt`.
- Recursive dependency resolution for npm and pip (MVP: downloading packages and wheels).
- Building a portable `.tar.zst` archive with `manifest.json` and `install.sh` for offline recovery.
- Basic integrity validation (sha256) and metadata.

---

## Quick start (local, dev) ▶️

### Requirements
- Python 3.8+
- pip
- GNU tar, zstd (or `python-zstandard`) for packaging (in the examples `tar` + `zstd` is used if available)
- (optional) Node.js/npm for testing npm functionality

### Installation (local dev environment) ✅
```bash
# Create and activate venv
python3 -m venv .venv
source .venv/bin/activate

# Install dev dependencies
pip install -U pip setuptools wheel
pip install -r requirements-dev.txt
