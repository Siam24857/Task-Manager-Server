# Vercel Deployment Guide

## Problem
The 500 error on `/api/auth/register/` is caused by SQLite database not working on Vercel (file system is ephemeral).

## Solution
Configure PostgreSQL database for production deployment.

## Steps to Fix

### 1. Set up PostgreSQL Database

**Option A: Vercel Postgres (Recommended)**
1. Go to Vercel dashboard
2. Navigate to your project
3. Go to Storage → Create Database → Postgres
4. Create a new Postgres database
5. Copy the connection string

**Option B: External PostgreSQL**
1. Use Supabase, Neon, or another PostgreSQL provider
2. Get your connection string

### 2. Configure Environment Variables on Vercel

Add these environment variables in Vercel project settings:

```
POSTGRES_HOST=your-postgres-host.vercel-storage.com
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=postgres
POSTGRES_PORT=5432
SECRET_KEY=your-secret-key-here
DEBUG=False
```

**For Vercel Postgres:**
- Vercel automatically provides `POSTGRES_URL` environment variable
- You can use it directly or extract individual values

### 3. Update Server Code (Already Done)

The following changes have been made:
- ✅ Added PostgreSQL configuration in `core/settings.py`
- ✅ Added `psycopg2-binary` to `requirements.txt`
- ✅ Added CORS configuration for Vercel domains
- ✅ Created `vercel_build.py` for automatic migrations
- ✅ Updated `vercel.json` to run migrations on build

### 4. Deploy to Vercel

1. Commit and push changes to Git
2. Vercel will automatically redeploy
3. The build process will run migrations automatically

### 5. Verify Deployment

Test the registration endpoint:
```bash
curl -X POST https://task-manager-server-one-sigma.vercel.app/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","password2":"testpass123"}'
```

## Local Development

For local development, the server will automatically use SQLite (no PostgreSQL needed):
```bash
python manage.py runserver
```

## Troubleshooting

### Migration Errors
If migrations fail, run them manually:
```bash
python manage.py migrate
```

### CORS Errors
Ensure your frontend URL is in `CORS_ALLOWED_ORIGINS` in settings.py

### Database Connection Errors
Check that all POSTGRES_* environment variables are set correctly in Vercel
