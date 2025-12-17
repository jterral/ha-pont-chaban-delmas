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
echo -e "✅ Pre-commit configuration completed."

# Python environment
echo -e "Setting up Python environment..."
$MISE python:init
echo -e "✅ Python environment setup completed."
