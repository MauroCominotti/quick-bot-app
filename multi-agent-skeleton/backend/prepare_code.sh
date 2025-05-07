#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.
set -u # Treat unset variables as an error when substituting.
set -o pipefail # Causes a pipeline to return the exit status of the last command.

echo "Starting prepare_code.sh script..."
echo "Current PATH: $PATH" # Log initial PATH

# --- Ensure Poetry command is available ---
if ! command -v poetry &> /dev/null
then
    echo "Poetry command not found by 'command -v'. Attempting installation..."
    # Ensure curl and python3 are available
    if ! command -v curl &> /dev/null || ! command -v python3 &> /dev/null; then
         echo "ERROR: curl or python3 not found. Cannot install Poetry."
         exit 1
    fi

    # Install using official installer
    echo "Running Poetry installer..."
    curl -sSL https://install.python-poetry.org | python3 -
    echo "Poetry installation script finished."

    # Determine the likely installation directory based on Cloud Build environment
    # The installer log previously indicated /builder/home/.local/bin
    POETRY_BIN_DIR=""
    if [ -d "/builder/home/.local/bin" ] && [ -x "/builder/home/.local/bin/poetry" ]; then
        POETRY_BIN_DIR="/builder/home/.local/bin"
        echo "Found Poetry executable in expected Cloud Build path: $POETRY_BIN_DIR"
    elif [ -d "$HOME/.local/bin" ] && [ -x "$HOME/.local/bin/poetry" ]; then
        # Check $HOME/.local/bin as a fallback (might be /root/.local/bin)
        POETRY_BIN_DIR="$HOME/.local/bin"
        echo "Found Poetry executable in fallback path: $POETRY_BIN_DIR (HOME is $HOME)"
    else
        echo "ERROR: Poetry installed but executable not found in expected locations (/builder/home/.local/bin or $HOME/.local/bin)."
        # Add more debug checks if needed
        ls -la /builder/home/.local/bin /root/.local/bin /usr/local/bin 2>/dev/null || echo "Could not list potential bin dirs."
        exit 1
    fi

    # Add the found directory to the PATH for the rest of this script's execution
    echo "Prepending '$POETRY_BIN_DIR' to PATH for this script session."
    export PATH="$POETRY_BIN_DIR:$PATH"
    echo "Updated PATH: $PATH"

    # Verify again using command -v
    if ! command -v poetry &> /dev/null; then
        echo "ERROR: Poetry command still not found in PATH after attempting to set it."
        exit 1
    fi
    echo "Poetry is now available in PATH."

else
    echo "Poetry command already available in PATH."
fi

# --- Verify Poetry execution ---
echo "Verifying poetry command execution..."
poetry --version
echo "Cloning adk-samples..."
# https://github.com/google/adk-samples.git/adk-samples/agents/travel-concierge/travel_concierge # TODO: Pass this as a template parameter to generalize solution for any ADK agent
git clone https://github.com/google/adk-samples.git

echo "Copying files from adk-samples..."
cp -r adk-samples/agents/travel-concierge/travel_concierge ./travel_concierge
cp -r adk-samples/agents/travel-concierge/eval ./eval
cp adk-samples/agents/travel-concierge/pyproject.toml . # TODO: Installing dependencies might be necessary only for local and not AE deployment
# cp adk-samples/agents/travel-concierge/poetry.lock . # TODO: Double check this, poetry.lock does not exist on the ADK repo

echo "Running poetry install --with deployment..."
poetry install --with deployment

echo "Finished prepare_code.sh script."