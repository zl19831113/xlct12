#!/bin/bash

# Script to start the Flask application with a dynamic port
# Created on: 2025-04-02

# Define a list of ports to try
PORTS=(5002 5003 5004 5005 5006 5007 5008 5009 5010 5011 5012 5013 5014 5015)

# Function to check if a port is in use
is_port_in_use() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Find an available port
AVAILABLE_PORT=""
for PORT in "${PORTS[@]}"; do
    if ! is_port_in_use $PORT; then
        AVAILABLE_PORT=$PORT
        break
    fi
done

if [ -z "$AVAILABLE_PORT" ]; then
    echo "Error: Could not find an available port. Please free up one of these ports: ${PORTS[*]}"
    exit 1
fi

echo "Starting application on port $AVAILABLE_PORT..."

# Create a temporary modified app.py with the new port
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
cp app.py "app.py.original_$TIMESTAMP"
echo "Created backup of app.py to app.py.original_$TIMESTAMP"

# Use sed to replace the port numbers in the app.py file
sed -i.bak "s/app.run(host='0.0.0.0', port=5001)/app.run(host='0.0.0.0', port=$AVAILABLE_PORT)/" app.py
sed -i.bak "s/app.run(host='0.0.0.0', port=8080)/app.run(host='0.0.0.0', port=$((AVAILABLE_PORT+1)))/" app.py

echo "Modified app.py to use port $AVAILABLE_PORT"
echo "Starting application..."

# Start the Flask application
python3 app.py

# Restore the original app.py
mv "app.py.original_$TIMESTAMP" app.py
echo "Restored original app.py"
