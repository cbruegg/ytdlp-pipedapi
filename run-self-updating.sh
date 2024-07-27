#!/usr/bin/env sh

# Run the Flask app for 24 hours, then shut it down, then with pip install the latest version
# of yt-dlp, then restart the Flask app.
# Do this in a loop.

while true; do
  # Start the Flask app in the background
  echo "Starting the Flask app..."
  flask run &
  FLASK_PID=$!

  # Run the Flask app for 24 hours
  sleep 86400
#  sleep 15

  echo "Shutting down the Flask app..."
  kill $FLASK_PID

  echo "Updating yt-dlp..."
  pip install --upgrade yt-dlp
done