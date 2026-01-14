import os

# Use the PORT environment variable Render provides
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

workers = 1  # Reduce to 1 worker to save RAM on the Free Tier
threads = 2
timeout = 120
