#!/bin/bash

# BeatLyrics Local Development Setup Script

set -e

echo "🎵 Setting up BeatLyrics development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp secrets.example.env .env
    echo "⚠️  Please edit .env file with your API keys before continuing."
    echo "   Required: OPENAI_API_KEY"
    echo "   Optional: YOUTUBE_API_KEY, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET"
    read -p "Press Enter after updating .env file..."
fi

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if backend is ready
echo "🔍 Checking backend health..."
until curl -f http://localhost:8000/health > /dev/null 2>&1; do
    echo "   Backend not ready yet, waiting..."
    sleep 5
done

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec backend alembic upgrade head

# Create S3 bucket
echo "📦 Setting up S3 bucket..."
docker-compose exec backend python -c "
import boto3
from botocore.exceptions import ClientError
s3 = boto3.client('s3', endpoint_url='http://minio:9000', aws_access_key_id='minioadmin', aws_secret_access_key='minioadmin')
try:
    s3.create_bucket(Bucket='beatlyrics')
    print('✅ S3 bucket created successfully')
except ClientError as e:
    if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
        print('✅ S3 bucket already exists')
    else:
        print(f'❌ Error creating S3 bucket: {e}')
"

# Seed sample data
echo "🌱 Seeding sample audio files..."
docker-compose exec backend python scripts/seed_samples.py

echo ""
echo "🎉 BeatLyrics is ready!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo "🗄️  MinIO Console: http://localhost:9001 (admin/minioadmin)"
echo ""
echo "🛑 To stop: docker-compose down"
echo "🔄 To restart: docker-compose restart"
echo "📋 To view logs: docker-compose logs -f [service-name]"
