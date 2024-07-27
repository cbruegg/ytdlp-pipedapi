#!/usr/bin/env sh

# Run the Flask app for 24 hours, then shut it down, then with pip install the latest version
# of yt-dlp, then restart the Flask app.
# Do this in a loop.

while true; do
  # Start the Flask app in the background
  workers=$(($(nproc) * 2))
  echo "Starting the Flask app with $workers workers..."
  gunicorn -w "$workers" "main:app" -b "0.0.0.0:5000" &
  FLASK_PID=$!

  # Run the Flask app for 24 hours
  sleep 86400
#  sleep 15

  echo "Shutting down the Flask app..."
  kill $FLASK_PID

  echo "Updating yt-dlp..."
  pip install --upgrade yt-dlp
done