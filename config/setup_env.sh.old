#!/bin/bash

# Source the .env file
set -a
source .env
set +a

# Create aliases
alias python=$PYTHON
alias pip=$PIP

# Activate virtual environment if it exists
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
fi

# Add src to PYTHONPATH
export PYTHONPATH=$PYTHONPATH

echo "Environment setup complete!"
echo "Python version: $(python3 --version)"
echo "Pip version: $(pip3 --version)"
echo "Virtual environment: $VIRTUAL_ENV"
