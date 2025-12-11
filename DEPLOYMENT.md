# Backend Deployment Instructions

## Current Status
❌ Backend is NOT deployed to Azure yet.

Your frontend is trying to connect to:
`https://student-application-backend-axeuh0g7bmcuema2.centralindia-01.azurewebsites.net`

But this backend doesn't exist yet or isn't running.

## Option 1: Deploy Backend to Azure (Recommended)

### Prerequisites:
1. **Azure Account** with an App Service for Python
2. **GitHub Secrets** configured:
   - `AZURE_WEBAPP_PUBLISH_PROFILE_BACKEND` - Download from Azure Portal

### Steps to Deploy:

1. **Create Azure App Service for Backend** (if not already created):
   - Go to Azure Portal
   - Create a new Web App
   - Name: `student-application-backend`
   - Runtime: Python 3.11
   - Region: Central India

2. **Download Publish Profile**:
   - Go to your backend App Service in Azure
   - Click "Download publish profile"
   - Save the XML file

3. **Add GitHub Secret**:
   - Go to your backend repository: `https://github.com/anildhami49/[YOUR-BACKEND-REPO]/settings/secrets/actions`
   - Click "New repository secret"
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE_BACKEND`
   - Value: Paste the entire contents of the publish profile XML
   - Click "Add secret"

4. **Configure Azure App Settings**:
   Go to Azure Portal → Your Backend App Service → Configuration → Application settings
   
   Add these settings:
   ```
   MONGO_URI = your-mongodb-connection-string
   MONGO_DB_NAME = user_management_db
   SECRET_KEY = your-secure-secret-key-here
   SCM_DO_BUILD_DURING_DEPLOYMENT = true
   ```

5. **Push to Deploy**:
   ```bash
   cd backend
   git add .
   git commit -m "Add Azure deployment configuration"
   git push origin main
   ```

6. **Monitor Deployment**:
   - Watch GitHub Actions: `https://github.com/anildhami49/[YOUR-BACKEND-REPO]/actions`
   - Check Azure logs: App Service → Monitoring → Log stream

7. **Test Backend**:
   ```
   https://student-application-backend-axeuh0g7bmcuema2.centralindia-01.azurewebsites.net/api/health
   ```

## Option 2: Use Local Backend (For Testing Only)

If you just want to test locally:

1. **Update Frontend Config** to use localhost:
   ```javascript
   // In frontend/public/config.js
   const PRODUCTION_API_URL = 'http://localhost:5000/api';
   ```

2. **Start Backend Locally**:
   ```bash
   cd backend
   python app.py
   ```

3. **Start Frontend Locally**:
   ```bash
   cd frontend
   npm start
   ```

## Files Created for Deployment:

- `.github/workflows/backend-deploy.yml` - GitHub Actions workflow
- `Procfile` - Tells Azure how to run the app
- `startup.sh` - Startup script for Azure
- Updated `requirements.txt` - Added gunicorn
- Updated `app.py` - Configured CORS for your frontend domain

## Troubleshooting:

### Backend shows 404:
- Backend isn't deployed or isn't running
- Check Azure App Service status
- Check deployment logs

### CORS errors:
- Frontend domain not in CORS allowed origins
- Already fixed in `app.py`

### MongoDB connection errors:
- Check `MONGO_URI` in Azure App Settings
- Ensure MongoDB allows connections from Azure IPs
- For MongoDB Atlas: Add 0.0.0.0/0 to IP whitelist (or Azure IPs)

## What's Next?

Choose one option:
- **Deploy backend to Azure** (recommended for production)
- **Test locally** (for development)

After backend is running, test your full application flow!
