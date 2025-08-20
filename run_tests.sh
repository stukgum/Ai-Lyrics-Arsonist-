#!/bin/bash

# BeatLyrics Test Runner

set -e

echo "🧪 Running BeatLyrics test suite..."

# Frontend tests
echo "🎨 Running frontend tests..."
npm test

# Backend tests
echo "🔧 Running backend tests..."
docker-compose exec backend pytest tests/ -v

# Integration tests
echo "🔗 Running integration tests..."
docker-compose exec backend pytest tests/integration/ -v

# Audio processing tests
echo "🎵 Running audio processing tests..."
docker-compose exec backend pytest tests/audio/ -v

echo "✅ All tests completed!"
