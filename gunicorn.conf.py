import os

# Render provides the port via the PORT environment variable
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

# Crucial for Free Tier: Only 1 worker to stay under 512MB RAM
workers = 1
threads = 2
timeout = 120
loglevel = "info"
accesslog = "-"
errorlog = "-"
