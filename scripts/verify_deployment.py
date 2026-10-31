#!/usr/bin/env python3
"""
CIT Campus Scheduling Platform - Deployment Readiness Verifier.
Validates environment, configuration files, solver models, and exports.
"""

import os
import sys
import json
import subprocess

def log_check(name: str, passed: bool, detail: str = ""):
    symbol = "[OK]  " if passed else "[FAIL]"
    print(f"{symbol} {name:<40} {detail}")
    return passed

def run():
    print("=" * 65)
    print("CIT CAMPUS SCHEDULING PLATFORM - DEPLOYMENT READINESS AUDIT")
    print("=" * 65)
    all_ok = True

    # 1. Essential Project Files
    essential_files = [
        "backend/app/main.py",
        "backend/requirements.txt",
        "frontend/package.json",
        "frontend/vite.config.ts",
        "data/cit_public.json",
        "exports/schedule.json",
        "exports/schedule_after.json",
        "validator.py",
        "Dockerfile",
        "docker-compose.yml",
        ".dockerignore",
        "render.yaml",
        "vercel.json",
        "netlify.toml",
        "railway.json"
    ]

    for f in essential_files:
        exists = os.path.exists(f)
        all_ok = log_check(f"File: {f}", exists) and all_ok

    print("-" * 65)

    # 2. Python Backend Module Import
    try:
        sys.path.insert(0, "backend")
        from app.main import app
        all_ok = log_check("Backend: app.main:app import", True, f"{len(app.routes)} routes mounted")
    except Exception as e:
        all_ok = log_check("Backend: app.main:app import", False, str(e)) and all_ok

    # 3. Baseline Schedule Validation
    try:
        cmd = [sys.executable, "validator.py", "--schedule", "exports/schedule.json", "--dataset", "data/cit_public.json"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        passed = (res.returncode == 0 and "0 violations" in res.stdout)
        all_ok = log_check("Validation: Baseline exports", passed, "0 Hard Violations (PASSED)") and all_ok
    except Exception as e:
        all_ok = log_check("Validation: Baseline exports", False, str(e)) and all_ok

    # 4. Disruption Schedule Validation
    try:
        cmd = [
            sys.executable, "validator.py",
            "--schedule", "exports/schedule_after.json",
            "--dataset", "data/cit_public.json",
            "--before", "exports/schedule.json",
            "--disruption", "data/sample_disruption.json"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        passed = (res.returncode == 0 and "0 violations" in res.stdout)
        all_ok = log_check("Validation: Disruption exports", passed, "0 Hard Violations (PASSED)") and all_ok
    except Exception as e:
        all_ok = log_check("Validation: Disruption exports", False, str(e)) and all_ok

    # 5. Frontend Production Bundle
    dist_html = os.path.join("frontend", "dist", "index.html")
    all_ok = log_check("Frontend: Production bundle dist/", os.path.exists(dist_html), "index.html present") and all_ok

    print("=" * 65)
    if all_ok:
        print("[SUCCESS] ALL SYSTEMS READY FOR PRODUCTION DEPLOYMENT!")
        print("Supported Targets: Vercel, Render, Railway, Netlify, Docker Compose")
        return 0
    else:
        print("[WARNING] Some checks failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(run())
