# OfflinePack — Portable Offline Dependency Packs

OfflinePack is a CLI tool to generate portable offline packages of project dependencies for common ecosystems (MVP: npm + pip). It collects dependencies, downloads their artifacts, produces a reproducible pack (tar.gz) and a simple installer stub so the project can be restored or installed in an environment without internet access.

Why OfflinePack 🤷‍♂️
- Make projects reproducible in air-gapped or low-connectivity environments.
- Prepare offline bundles for hackathons, training labs, or branches with blocked networks.
- Save time for SREs and devs who need portable, verifiable dependency archives.

Key features (MVP) 🧪
- Read package.json and requirements.txt
- Resolve top-level dependencies (npm + pip) and fetch artifact files (npm tarballs and pip wheels/sdists)
- Create a tar.gz bundle containing:
  - packages/ (downloaded artifacts)
  - manifest.json (pack metadata and checksums)
  - install.sh (simple installer to install from the local files)
- Basic checksum validation (sha256) and manifest recording

Quick start (example) 🟩

1. Install Go (1.20+), clone repository, build:
   go build -o offlinepack ./cmd/offlinepack

2. Prepare a project with package.json and/or requirements.txt

3. Create an offline pack:
   ./offlinepack pack --project /path/to/project --out /path/to/out/offline-pack.tar.gz

4. On the offline machine, extract and run installer:
   tar -xzf offline-pack.tar.gz
   ./install.sh

Usage (CLI) 🟩
- pack: read manifests and produce offline pack
  ./offlinepack pack --project <project-dir> --out <output-file>

Flags
- --project : path to project folder (contains package.json and/or requirements.txt)
- --out     : output archive path (defaults to offline-pack.tar.gz)
- --tmp     : temporary working directory (optional)

Installer (generated) 🟩
- install.sh will:
  - Install pip packages from local packages/ directory using pip --no-index --find-links
  - Install npm packages from local tarballs via npm install ./packages/*.tgz (best-effort)
  - Provide instructions in case of manual steps


Example workflow 🔬

1. Developer runs offlinepack pack -> generates offline-pack.tar.gz

2. Copy the pack to offline host (USB / internal file server)

3. Extract and run install.sh to restore runtime dependencies

Contact / Support
- Open an issue in the GitHub repository for bugs or feature requests.
