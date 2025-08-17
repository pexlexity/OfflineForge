#!/usr/bin/env python3
"""
firstpush.sh — Python script to initialize a local repo and push to remote.

Usage:
  ./firstpush.sh [--repo <REPOURL>] [--branch <branch>]

Defaults:
  REPOURL: https://github.com/pexlexity/OfflineForge.git
  BRANCH: main

Signature: Pexlexity
"""
import argparse
import os
import subprocess
import sys
import shutil
from textwrap import dedent

REPO_DEFAULT = "https://github.com/pexlexity/OfflineForge.git"
BRANCH_DEFAULT = "main"

def run(cmd, check=True, capture=False):
    if isinstance(cmd, (list,tuple)):
        proc = subprocess.run(cmd, check=check, stdout=subprocess.PIPE if capture else None, stderr=subprocess.STDOUT if capture else None, text=True)
    else:
        proc = subprocess.run(cmd, shell=True, check=check, stdout=subprocess.PIPE if capture else None, stderr=subprocess.STDOUT if capture else None, text=True)
    return proc

def git_available():
    return shutil.which("git") is not None

def safe_git_init():
    if not os.path.isdir(".git"):
        print("[*] git init")
        run(["git","init"])
    else:
        print("[*] git repository already initialized")

def git_add_all():
    print("[*] git add .")
    run(["git","add","--all"])

def git_commit(msg="Initial commit"):
    # if there are no staged changes, skip
    st = run(["git","status","--porcelain"], capture=True)
    if st.stdout.strip() == "":
        print("[*] nothing to commit")
        return False
    run(["git","commit","-m", msg])
    print("[+] commit created")
    return True

def git_set_remote(url):
    # if origin exists, update it
    res = run(["git","remote"], capture=True)
    if "origin" in (res.stdout or ""):
        print("[*] updating origin")
        run(["git","remote","set-url","origin",url])
    else:
        print("[*] adding origin")
        run(["git","remote","add","origin",url])

def git_push(branch):
    print(f"[*] pushing to origin {branch} ...")
    try:
        run(["git","branch","-M", branch])
    except Exception:
        pass
    run(["git","push","-u","origin",branch])
    print("[+] push finished")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("REPOURL", REPO_DEFAULT))
    parser.add_argument("--branch", default=os.environ.get("BRANCH", BRANCH_DEFAULT))
    parser.add_argument("--message", default="Initial commit (OfflineForge)")
    args = parser.parse_args()

    print(dedent(f"""
    ============================================
      OfflineForge — first push helper
      Author: Pexlexity
    ============================================
    """))

    if not git_available():
        print("Error: git is not installed. Install git and retry.")
        sys.exit(1)

    safe_git_init()

    # ensure user has configured name/email (helpful hint)
    cfg_name = run(["git","config","user.name"], capture=True)
    if not cfg_name.stdout.strip():
        print("[!] git user.name not set. Setting a placeholder 'Pexlexity'.")
        run(["git","config","user.name","Pexlexity"])
    cfg_email = run(["git","config","user.email"], capture=True)
    if not cfg_email.stdout.strip():
        print("[!] git user.email not set. Setting a placeholder 'you@example.com'.")
        run(["git","config","user.email","you@example.com"])

    # Add files & commit
    git_add_all()
    committed = git_commit(args.message)

    # set remote and push
    git_set_remote(args.repo)

    # attempt push with retries and helpful error messages
    try:
        git_push(args.branch)
    except subprocess.CalledProcessError as e:
        print("Push failed. Common reasons:")
        print(" - No access to remote (use SSH key or PAT).")
        print(" - Remote already exists and has commits (consider pulling or force push with caution).")
        print("See instructions in README for SSH / PAT setup.")
        sys.exit(2)

    print("\n" + "="*40)
    print("All done — repository initialized and pushed.")
    print("Signature: Pexlexity")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
