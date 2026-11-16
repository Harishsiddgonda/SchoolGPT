# SchoolGPT - Render Cloud & Mobile Deployment Guide
### RSR Technologies Enterprise AI Platform

---

## Part 1: Render Cloud Deployment (Web + API + Database)

### 1. Prerequisites
- An active [Render.com](https://render.com) account.
- A GitHub account with the repository pushed: `https://github.com/Harishsiddgonda/schoolgpt-rsr-technologies.git`.
- A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/).

### 2. Deploy via Render Blueprint
1. In your Render Dashboard, click **New +** → **Blueprint**.
2. Connect your GitHub repository: `schoolgpt-rsr-technologies`.
3. Render will read `render.yaml` and configure three synchronized services:
   - **`schoolgpt-api`** (Web Service):
     - Runtime: Python 3.12
     - Build: `pip install -r requirements.txt`
     - Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
     - Health Check: `/health`
   - **`schoolgpt-web`** (Static Site):
     - Build: `cd apps/web && npm install && npm run build`
     - Publish Directory: `apps/web/dist`
   - **`schoolgpt-db`** (Managed PostgreSQL):
     - Database: `schoolgpt`
     - Version: PostgreSQL 16 with `pgvector` extension

### 3. Environment Variables Configuration on Render
In the **`schoolgpt-api`** service settings, supply the following environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API Key (e.g. `AIzaSy...`).
- `AI_PROVIDER`: `gemini`
- `GEMINI_MODEL`: `gemini-1.5-flash`
- `SECRET_KEY`: Automatically generated or custom 32-character string.
- `DATABASE_URL`: Automatically linked from `schoolgpt-db`.
- *(Optional)* `S3_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` for persistent cloud document storage.

---

## Part 2: Android Mobile APK Generation (Expo EAS)

Once your Render backend is deployed and you have your live URL (e.g., `https://schoolgpt-api.onrender.com`):

### 1. Configure the Live Backend URL
Open `apps/mobile/src/api/mobileClient.ts` (or set the environment variable):
```bash
EXPO_PUBLIC_API_BASE_URL=https://schoolgpt-api.onrender.com/api/v1
```

### 2. Run EAS Standalone APK Build
1. Install Expo Application Services (EAS) CLI:
   ```bash
   npm install -g eas-cli
   ```
2. Log in to Expo:
   ```bash
   eas login
   ```
3. Run the APK preview build:
   ```bash
   cd apps/mobile
   eas build -p android --profile preview
   ```
4. EAS builds the `.apk` in the cloud and provides a direct download link.
5. Transfer the APK to an Android smartphone and tap to install!
