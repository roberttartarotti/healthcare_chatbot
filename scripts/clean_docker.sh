#!/bin/bash

echo "🧹 Cleaning Docker environment..."

echo "📦 Stopping all running containers..."
docker stop $(docker ps -aq) 2>/dev/null || echo "No running containers to stop"

echo "🗑️  Removing all containers..."
docker rm $(docker ps -aq) 2>/dev/null || echo "No containers to remove"

echo "🖼️  Removing all images..."
docker rmi $(docker images -q) 2>/dev/null || echo "No images to remove"

echo "💾 Removing all volumes..."
docker volume rm $(docker volume ls -q) 2>/dev/null || echo "No volumes to remove"

echo "🌐 Removing custom networks..."
docker network prune -f

echo "🧽 Cleaning up unused Docker data..."
docker system prune -af

echo "🔍 Removing dangling images..."
docker image prune -af

echo "✅ Docker environment cleaned successfully!"
echo "💡 You can now start fresh with: docker-compose up" 