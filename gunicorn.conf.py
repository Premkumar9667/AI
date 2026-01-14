import os

# Render provides the PORT environment variable (usually 10000)
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

workers = 2 
threads = 4 
timeout = 120 
loglevel = "info" 
accesslog = "-" 
errorlog = "-"
