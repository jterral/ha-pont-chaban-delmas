#!/usr/bin/env bash

set -e

echo -e "🔧 Installing project dependencies..."

# Mise
echo -e "Setting up mise environment..."
MISE=$(which mise)
$MISE trust .
echo "eval \"\$($MISE activate bash)\"" >> ~/.bashrc
echo -e "✅ Mise environment setup completed."
