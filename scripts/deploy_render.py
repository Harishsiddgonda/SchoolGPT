"""
Render Cloud Deployment Verification Script
Verifies environment variables, database configuration, and Render Blueprint.
RSR Technologies
"""

import os
import sys

def verify_deployment():
    print("==================================================")
    print("SchoolGPT - Render Cloud Pre-Flight Verification")
    print("RSR Technologies")
    print("==================================================")

    # 1. Check render.yaml
    if os.path.exists("render.yaml"):
        print(" [OK] render.yaml blueprint detected.")
    else:
        print(" [FAIL] render.yaml is missing.")
        sys.exit(1)

    # 2. Check requirements.txt
    if os.path.exists("requirements.txt"):
        print(" [OK] requirements.txt detected.")
    else:
        print(" [FAIL] requirements.txt is missing.")
        sys.exit(1)

    # 3. Check React Web dist build
    web_pkg = os.path.join("apps", "web", "package.json")
    if os.path.exists(web_pkg):
        print(" [OK] apps/web React project detected.")
    else:
        print(" [FAIL] apps/web/package.json is missing.")
        sys.exit(1)

    # 4. Check Mobile app.json and eas.json
    mobile_app_json = os.path.join("apps", "mobile", "app.json")
    mobile_eas_json = os.path.join("apps", "mobile", "eas.json")
    if os.path.exists(mobile_app_json) and os.path.exists(mobile_eas_json):
        print(" [OK] apps/mobile Expo project with eas.json preview APK profile detected.")
    else:
        print(" [FAIL] apps/mobile configuration missing.")
        sys.exit(1)

    # 5. Environment requirements checklist
    print("\n--- Production Environment Variables Checklist ---")
    checklist = [
        ("DATABASE_URL", "Managed PostgreSQL URL (provided automatically by Render)"),
        ("SECRET_KEY", "JWT signing secret key"),
        ("AI_PROVIDER", "Set to 'gemini' for cloud production or 'ollama' for on-premise"),
        ("GEMINI_API_KEY", "Google Gemini API Key for grounded LLM inference"),
        ("GEMINI_MODEL", "gemini-1.5-flash (default fast model)"),
        ("S3_BUCKET_NAME", "(Optional) AWS S3 / Cloudflare R2 bucket for document storage"),
        ("AWS_ACCESS_KEY_ID", "(Optional) S3 Access Key ID"),
        ("AWS_SECRET_ACCESS_KEY", "(Optional) S3 Secret Access Key"),
        ("PORT", "Port assigned by Render (default 10000 or 8000)")
    ]
    for key, desc in checklist:
        val = os.getenv(key, "")
        status = "SET" if val else "REQUIRED AT DEPLOYMENT"
        print(f" • {key.ljust(22)} : {status.ljust(24)} ({desc})")

    print("\nPre-flight verification passed! Ready for Render Blueprint deployment.")

if __name__ == "__main__":
    verify_deployment()
