# Backend Deployment Instructions

## ⚠️ IMPORTANT: Azure Configuration Required

Your backend URL returns "resource not found" because:
1. Backend app service exists but has no code deployed yet, OR
2. Startup command isn't configured in Azure, OR
3. GitHub secret for deployment isn't set up

## 🚀 Complete Deployment Steps

### Step 1: Configure Azure App Service Settings

Go to Azure Portal → `student-application-backend` → Configuration

#### A. Application Settings (Add these):
```
MONGO_URI = your-mongodb-atlas-connection-string
MONGO_DB_NAME = user_management_db
SECRET_KEY = your-random-secure-key-min-32-chars
SCM_DO_BUILD_DURING_DEPLOYMENT = true
WEBSITES_PORT = 8000
```

**To get MONGO_URI:**
- MongoDB Atlas → Connect → Drivers → Copy connection string
- Replace `<password>` with your actual password
- Example: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`

#### B. General Settings:
- **Stack**: Python
- **Python version**: 3.11
- **Startup Command**: `gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=600 app:app`

**HOW TO SET:**
1. Go to Configuration → General settings
2. Find "Startup Command" field
3. Paste: `gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=600 app:app`
4. Click Save

### Step 2: Set Up GitHub Actions Secret

1. **Download Publish Profile:**
   - Azure Portal → `student-application-backend`
   - Click "Download publish profile" (top menu)
   - Save the `.PublishSettings` file

2. **Add GitHub Secret:**
   - Go to: https://github.com/anildhami49/User-management-Backend/settings/secrets/actions
   - Click "New repository secret"
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE_BACKEND`
   - Value: Open the downloaded file and copy ALL contents (entire XML)
   - Click "Add secret"

### Step 3: Trigger Deployment

**Option A: Automatic (Already triggered by last push)**
- Check: https://github.com/anildhami49/User-management-Backend/actions
- Wait for deployment to complete (~3-5 minutes)

**Option B: Manual Trigger**
```bash
cd backend
git add .
git commit -m "Update deployment configuration"
git push origin main
```

Or use GitHub Actions → "Deploy Backend to Azure Web App" → Run workflow

### Step 4: Verify Deployment

**Test these URLs:**

1. **Root**: https://student-application-backend-axeuh0g7bmcuema2.centralindia-01.azurewebsites.net/
   - Should return JSON with API info

2. **Health**: https://student-application-backend-axeuh0g7bmcuema2.centralindia-01.azurewebsites.net/api/health
   - Should return: `{"status": "healthy", "message": "Backend is running!"}`

3. **From Frontend**: Try signing up a user

### Step 5: Monitor Logs (if issues persist)

**View Live Logs:**
1. Azure Portal → `student-application-backend`
2. Monitoring → Log stream
3. Watch for errors during startup

**Common Errors:**

❌ **"ModuleNotFoundError"**
- Solution: Check if `SCM_DO_BUILD_DURING_DEPLOYMENT = true` is set
- Force rebuild: Deployment Center → Redeploy

❌ **"MongoDB connection failed"**
- Solution: Check MONGO_URI in Application Settings
- Verify MongoDB Atlas IP whitelist includes Azure (0.0.0.0/0 or specific Azure IPs)

❌ **"Address already in use"**
- Solution: Set `WEBSITES_PORT = 8000` in Application Settings

❌ **"Application startup failed"**
- Solution: Verify Startup Command is set correctly

## Alternative: Quick Manual Deployment (For Testing)

If GitHub Actions isn't working:

1. **Zip your backend code:**
   ```powershell
   cd backend
   Compress-Archive -Path * -DestinationPath backend-deploy.zip -Force -Exclude .git,.github,venv,.env,__pycache__,*.pyc,test_api.py
   ```

2. **Deploy via Azure Portal:**
   - Go to Deployment Center
   - Choose "Local Git" or "ZIP Deploy"
   - Upload `backend-deploy.zip`

## What I've Configured:

✅ CORS - Allows requests from your frontend domain
✅ Gunicorn - Production WSGI server
✅ Root endpoint - For Azure health checks
✅ Startup script - Proper Azure configuration
✅ GitHub Actions - Automated deployment workflow

## Next Steps:

1. ✅ Set Azure Application Settings (MONGO_URI, SECRET_KEY, etc.)
2. ✅ Set Startup Command in Azure
3. ✅ Add GitHub Secret (AZURE_WEBAPP_PUBLISH_PROFILE_BACKEND)
4. ✅ Wait for deployment or trigger manually
5. ✅ Test backend URLs
6. ✅ Test full application from frontend
