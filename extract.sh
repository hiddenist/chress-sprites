#!/bin/bash
# Sprite extraction script wrapper
# Automatically sets up Python virtual environment and runs the extraction script

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VENV_DIR="venv"
SCRIPT="src/extract_sprites.py"

echo "Sprite Sheet Extractor"
echo "======================"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}Virtual environment created!${NC}"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check if Pillow is installed
if ! python -c "import PIL" 2>/dev/null; then
    echo -e "${YELLOW}Installing required dependencies (Pillow)...${NC}"
    pip install --quiet Pillow
    echo -e "${GREEN}Dependencies installed!${NC}"
    echo ""
fi

# Run the extraction script with any passed arguments
echo "Running sprite extraction..."
echo ""
python "$SCRIPT" "$@"

# Deactivate virtual environment
deactivate

echo ""
echo -e "${GREEN}Done!${NC}"