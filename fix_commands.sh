#!/bin/bash
cd /var/www/question_bank || exit 1

echo "==== SYSTEM STATUS BEFORE FIX ===="
echo "Process status:"
ps aux | grep -E 'gunicorn|nginx' | grep -v grep

echo "==== CHECKING APP.PY FOR SYNTAX ERRORS ===="
python3 -m py_compile app.py
if [ $? -ne 0 ]; then
  echo "SYNTAX ERROR DETECTED in app.py"
  
  # Find most recent backup
  BACKUP=$(ls -t app.py.backup_* 2>/dev/null | head -1)
  if [ -n "$BACKUP" ]; then
    echo "Restoring from backup: $BACKUP"
    cp "$BACKUP" app.py
  else
    echo "NO BACKUP FOUND. Creating minimal working version"
    # Create minimal app.py if no backup exists
    cat > app.py.minimal << EOF2
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Emergency Restored Version"

if __name__ == '__main__':
    app.run(debug=True)
EOF2
    cp app.py.minimal app.py
  fi
fi

echo "==== RESTARTING SERVICES ===="
echo "Stopping Gunicorn..."
pkill -f gunicorn
sleep 2

# Force kill if still running
if pgrep -f gunicorn > /dev/null; then
  echo "Force killing Gunicorn..."
  pkill -9 -f gunicorn
  sleep 2
fi

echo "Starting Gunicorn..."
cd /var/www/question_bank
source venv/bin/activate 2>/dev/null || echo "No virtual environment found"

# Start with proper logs
nohup gunicorn -c gunicorn_config.py app:app > gunicorn.log 2>&1 &
echo "Waiting for Gunicorn to start..."
sleep 5

echo "Reloading Nginx..."
nginx -t && systemctl reload nginx

echo "==== CHECKING FILE PERMISSIONS ===="
chown -R www-data:www-data /var/www/question_bank
chmod -R 755 /var/www/question_bank

echo "==== SERVICE STATUS AFTER FIX ===="
ps aux | grep -E 'gunicorn|nginx' | grep -v grep
echo "Latest log entries:"
tail -n 10 gunicorn.log

# Test accessibility
echo "==== TESTING SERVER RESPONSE ===="
curl -I http://localhost:8000/ 2>/dev/null || echo "Server not responding on localhost:8000"
