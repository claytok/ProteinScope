#!/bin/bash

# ProteinScope Deployment Script

echo "🧬 ProteinScope Deployment"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root."
    exit 1
fi

echo "📋 Choose deployment option:"
echo "1. Deploy backend to Heroku"
echo "2. Deploy frontend to Netlify"
echo "3. Deploy both (full deployment)"
echo "4. Exit"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Deploying backend to Heroku..."
        
        # Check if Heroku CLI is installed
        if ! command -v heroku &> /dev/null; then
            echo "❌ Heroku CLI not found. Please install it first:"
            echo "   brew install heroku/brew/heroku"
            exit 1
        fi
        
        # Check if logged in
        if ! heroku auth:whoami &> /dev/null; then
            echo "🔐 Please log in to Heroku:"
            heroku login
        fi
        
        # Create app if it doesn't exist
        if [ -z "$HEROKU_APP_NAME" ]; then
            read -p "Enter Heroku app name (or press Enter to auto-generate): " app_name
            if [ -z "$app_name" ]; then
                heroku create
            else
                heroku create $app_name
            fi
        fi
        
        # Deploy
        echo "📦 Deploying to Heroku..."
        git add .
        git commit -m "Deploy to Heroku"
        git push heroku main
        
        # Get the URL
        echo "✅ Backend deployed!"
        echo "🌐 Backend URL: $(heroku info -s | grep web_url | cut -d= -f2)"
        echo "📝 Update the backend URL in static/js/app.js"
        ;;
        
    2)
        echo "🌐 Deploying frontend to Netlify..."
        
        # Create frontend directory
        if [ ! -d "frontend-deploy" ]; then
            mkdir frontend-deploy
        fi
        
        # Copy static files
        cp -r static/* frontend-deploy/
        
        # Create netlify.toml
        cat > frontend-deploy/netlify.toml << EOF
[build]
  publish = "."

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
EOF
        
        echo "✅ Frontend files prepared in 'frontend-deploy/'"
        echo "📝 Drag and drop the 'frontend-deploy' folder to Netlify"
        echo "🌐 Or connect your GitHub repository to Netlify"
        ;;
        
    3)
        echo "🚀 Full deployment..."
        
        # Deploy backend first
        echo "📦 Deploying backend..."
        if ! command -v heroku &> /dev/null; then
            echo "❌ Heroku CLI not found. Please install it first."
            exit 1
        fi
        
        if ! heroku auth:whoami &> /dev/null; then
            heroku login
        fi
        
        read -p "Enter Heroku app name (or press Enter to auto-generate): " app_name
        if [ -z "$app_name" ]; then
            heroku create
        else
            heroku create $app_name
        fi
        
        git add .
        git commit -m "Deploy to Heroku"
        git push heroku main
        
        backend_url=$(heroku info -s | grep web_url | cut -d= -f2)
        echo "✅ Backend deployed at: $backend_url"
        
        # Update frontend with backend URL
        echo "🔧 Updating frontend with backend URL..."
        sed -i '' "s|https://your-backend-url.herokuapp.com|$backend_url|g" static/js/app.js
        
        # Prepare frontend
        mkdir -p frontend-deploy
        cp -r static/* frontend-deploy/
        
        cat > frontend-deploy/netlify.toml << EOF
[build]
  publish = "."

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
EOF
        
        echo "✅ Frontend prepared in 'frontend-deploy/'"
        echo "📝 Deploy the 'frontend-deploy' folder to Netlify"
        echo "🌐 Backend URL: $backend_url"
        ;;
        
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment completed!"
echo "📖 For detailed instructions, see DEPLOYMENT.md" 