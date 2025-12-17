#!/usr/bin/env bash
set -e

echo -e "🚀 Starting devcontainer setup script..."

# Mise
echo -e "Setting up mise configuration..."
MISE=$(which mise)
$MISE info
echo -e "✅ Mise configuration completed."

# Pre-commit
$MISE precommit:configure

echo -e "Devcontainer setup script completed."
