# CRITICAL AZURE BACKEND CONFIGURATION NEEDED

## Problem: Backend shows "Service Unavailable" - Not Starting

The backend isn't starting because Azure is misconfigured. It's set as .NET instead of Python.

## ✅ SOLUTION: Reconfigure Azure App Service

### Step 1: Change Runtime Stack to Python

Go to: **Azure Portal** → **student-application-Backend** → **Settings** → **Configuration**

Look for **Stack settings** or **Runtime settings** and change:
- **Stack**: Python (not .NET!)
- **Python version**: 3.11
- **Startup Command**: Leave blank OR enter: `gunicorn --bind=0.0.0.0:$PORT --workers=1 --threads=4 --timeout=0 app:app`

### Step 2: Verify Environment Variables

In **Environment variables** → **App settings**, ensure you have:

```
WEBSITES_PORT = 8000
SCM_DO_BUILD_DURING_DEPLOYMENT = true
MONGO_URI = your-mongodb-connection-string
MONGO_DB_NAME = user_management_db
SECRET_KEY = your-secret-key
```

### Step 3: Restart the App Service

After making changes:
1. Click **Save**
2. Go to **Overview**
3. Click **Restart**
4. Wait 2 minutes

### Step 4: Test Backend

Visit: https://student-application-backend-axeuh0g7bmcuema2.centralindia-01.azurewebsites.net/

Should show JSON response, not "Service Unavailable"

## Alternative: Recreate App Service with Correct Stack

If you can't change the stack, you may need to:

1. **Create a NEW Azure App Service**:
   - Name: `student-application-backend-python` (or similar)
   - **Runtime stack**: Python 3.11
   - Region: Central India
   - Pricing: Free tier is fine

2. **Download NEW Publish Profile**:
   - From the new app service
   - Update GitHub secret `AZURE_WEBAPP_PUBLISH_PROFILE_BACKEND`

3. **Update Workflow**:
   - Change `AZURE_WEBAPP_NAME` in `.github/workflows/backend-deploy.yml`
   - To the new app name

4. **Redeploy**:
   - Push code to trigger deployment

## Why This Happened

When you created the backend App Service, it was set to .NET runtime instead of Python. Azure can't run Python code with a .NET runtime configuration.

## Next Steps

1. ✅ Change Azure App Service to Python 3.11 runtime
2. ✅ Add all environment variables
3. ✅ Restart the app
4. ✅ Test backend URL
5. ✅ Then test frontend signup
