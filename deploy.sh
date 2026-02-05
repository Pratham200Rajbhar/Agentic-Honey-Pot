#!/bin/bash

# --- Agentic Honey-Pot Deployment Script ---
# Automates PostgreSQL/Prisma setup and PM2 process management.

echo "🚀 Starting Agentic Honey-Pot Deployment..."

# 1. Environment Check
echo "🔍 Checking environment..."

if ! command -v python &> /dev/null; then
    echo "❌ Error: Python not found. Please install Python 3.9+."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm not found. Required for Prisma."
    exit 1
fi

# 2. Dependency Installation
echo "📦 Installing dependencies..."
python -m pip install -r requirements.txt

# 3. Database Sync (PostgreSQL via Prisma)
echo "🗄️ Synchronizing PostgreSQL schema with Prisma..."
if [ -f ".env" ]; then
    # Ensure prisma client is generated
    npx prisma generate
    
    # Push schema to database (automatically creates tables based on DATABASE_URL in .env)
    npx prisma db push
    
    if [ $? -eq 0 ]; then
        echo "✅ Database synchronized successfully."
    else
        echo "❌ Database synchronization failed. Please check your DATABASE_URL in .env."
        exit 1
    fi
else
    echo "❌ Error: .env file not found. Database synchronization skipped."
    exit 1
fi

# 4. PM2 Management
echo "⚙️ Configuring PM2 Process..."

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "⚠️ PM2 not found. Installing globally via npm..."
    npm install -g pm2
fi

# Stop existing process if it exists
pm2 stop honey-pot-api &> /dev/null || true
pm2 delete honey-pot-api &> /dev/null || true

# Start new process
echo "🟢 Starting honey-pot-api via PM2..."
pm2 start "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" --name "honey-pot-api"

if [ $? -eq 0 ]; then
    echo "✨ Deployment Complete! API is running in the background."
    echo "📋 Use 'pm2 status' to monitor the process."
    echo "📝 Use 'pm2 logs honey-pot-api' to view runtime logs."
    pm2 save
else
    echo "❌ Deployment failed during PM2 startup."
    exit 1
fi

echo "🛡️ Agentic Honey-Pot is now active."
