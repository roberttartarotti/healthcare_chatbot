#!/bin/bash
# Load environment variables from .env file into current shell session
# Usage: source ./scripts/load_env.sh

echo "📄 Loading environment variables from .env file..."

# Look for .env file in current directory and parent directory
ENV_FILE=""
if [ -f .env ]; then
    ENV_FILE=".env"
elif [ -f ../.env ]; then
    ENV_FILE="../.env"
else
    echo "❌ Error: .env file not found in current or parent directory!"
    echo "Please copy .env.example to .env and update the values:"
    echo "cp .env.example .env"
    return 1
fi

echo "📁 Found .env file: $ENV_FILE"

# Load environment variables, filtering out comments, empty lines, and section headers
while IFS= read -r line; do
    # Skip empty lines, comments, and section headers (lines with =====)
    if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# && ! "$line" =~ ^[[:space:]]*= && ! "$line" =~ ^[[:space:]]*$ ]]; then
        # Export the variable
        export "$line"
    fi
done < "$ENV_FILE"

echo "✅ Environment variables loaded successfully!"
echo "📊 Loaded variables:"
echo "   - RABBITMQ_USER: $RABBITMQ_USER"
echo "   - MONGODB_USER: $MONGODB_USER"
echo "   - MCP_PORT: $MCP_PORT"
echo "   - COMPOSE_PROJECT_NAME: $COMPOSE_PROJECT_NAME"
echo ""
echo "💡 Tip: Use 'source ./scripts/load_env.sh' to load variables into current shell"
