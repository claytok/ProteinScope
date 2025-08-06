# 🚀 Deployment Guide

This guide explains how to deploy ProteinScope to production.

## 📋 Overview

The application consists of two parts:
- **Backend**: Flask API (Python)
- **Frontend**: Static HTML/CSS/JS (Netlify)

## 🎯 Option 1: Full Deployment (Recommended)

### Step 1: Deploy Backend

Choose one of these platforms:

#### A. Heroku (Free Tier Available)

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   heroku login
   heroku create your-protein-visualizer-backend
   ```

3. **Add Buildpacks**
   ```bash
   heroku buildpacks:set heroku/python
   ```

4. **Create Procfile**
   ```bash
   echo "web: gunicorn app:app" > Procfile
   ```

5. **Update requirements.txt**
   ```bash
   echo "gunicorn>=20.0.0" >> requirements.txt
   ```

6. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

7. **Get your backend URL**
   ```bash
   heroku info -s | grep web_url
   # Example: https://your-app-name.herokuapp.com
   ```

#### B. Railway (Free Tier Available)

1. **Go to [Railway.app](https://railway.app)**
2. **Connect your GitHub repository**
3. **Select the repository**
4. **Railway will auto-detect Python and deploy**
5. **Get your backend URL from Railway dashboard**

#### C. Render (Free Tier Available)

1. **Go to [Render.com](https://render.com)**
2. **Create new Web Service**
3. **Connect your GitHub repository**
4. **Set build command**: `pip install -r requirements.txt`
5. **Set start command**: `gunicorn app:app`
6. **Deploy and get your backend URL**

### Step 2: Update Frontend Backend URL

1. **Edit `static/js/app.js`**
   ```javascript
   // Change this line:
   return 'https://your-backend-url.herokuapp.com'; // CHANGE THIS
   
   // To your actual backend URL:
   return 'https://your-app-name.herokuapp.com';
   ```

### Step 3: Deploy Frontend to Netlify

1. **Create a new repository structure for frontend only:**
   ```bash
   mkdir protein-visualizer-frontend
   cd protein-visualizer-frontend
   cp -r ../PyMOL2/static/* .
   ```

2. **Create `netlify.toml`**
   ```toml
   [build]
     publish = "."
   
   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```

3. **Deploy to Netlify:**
   - Go to [Netlify.com](https://netlify.com)
   - Drag and drop the `protein-visualizer-frontend` folder
   - Or connect your GitHub repository

## 🎯 Option 2: Static-Only Deployment (Limited)

If you want to deploy just the frontend without a backend:

1. **Remove backend dependency from `static/js/app.js`:**
   ```javascript
   getBackendUrl() {
       return null; // No backend
   }
   ```

2. **Add demo data:**
   ```javascript
   async analyzeProtein() {
       // Show demo data instead of real analysis
       this.showDemoResults();
   }
   ```

3. **Deploy to Netlify as static site**

## 🔧 Configuration Files

### For Heroku Backend

Create `Procfile`:
```
web: gunicorn app:app
```

Update `requirements.txt`:
```
flask>=2.0.0
biopython>=1.80
numpy>=1.20.0
matplotlib>=3.5.0
plotly>=5.0.0
requests>=2.25.0
pandas>=1.3.0
scipy>=1.7.0
gunicorn>=20.0.0
```

### For Netlify Frontend

Create `netlify.toml`:
```toml
[build]
  publish = "."

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

## 🌐 Environment Variables

For the backend, you might need to set:

```bash
# Heroku
heroku config:set FLASK_ENV=production

# Railway/Render
# Set in their respective dashboards
```

## 🔍 Testing Your Deployment

1. **Test Backend:**
   ```bash
   curl https://your-backend.herokuapp.com/examples
   ```

2. **Test Frontend:**
   - Open your Netlify URL
   - Check if backend status shows "connected"
   - Try analyzing a protein

## 🚨 Common Issues

### CORS Errors
If you get CORS errors, add to your Flask app:
```python
from flask_cors import CORS
CORS(app)
```

### Backend Not Responding
- Check if your backend URL is correct in `static/js/app.js`
- Verify your backend is running
- Check logs: `heroku logs --tail`

### 3D Visualization Not Working
- Ensure Plotly.js is loaded
- Check browser console for errors
- Verify the plot data format

## 📊 Monitoring

### Backend Monitoring
- **Heroku**: `heroku logs --tail`
- **Railway**: Dashboard logs
- **Render**: Dashboard logs

### Frontend Monitoring
- **Netlify**: Analytics in dashboard
- **Browser**: Developer tools console

## 🔄 Updates

### Update Backend
```bash
git add .
git commit -m "Update backend"
git push heroku main
```

### Update Frontend
- Push to GitHub (if connected)
- Or drag and drop new files to Netlify

## 💡 Tips

1. **Use environment variables** for sensitive data
2. **Test locally** before deploying
3. **Monitor logs** for errors
4. **Use HTTPS** for production
5. **Set up CI/CD** for automatic deployments

## 🆘 Support

If you encounter issues:
1. Check the logs
2. Verify URLs are correct
3. Test endpoints individually
4. Check browser console for errors 