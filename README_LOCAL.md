# Prem Kumar's AI Engineer Portfolio - Local Setup

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

## Local Installation & Setup

### 1. Download the Project
Download or clone all the project files to your local directory.

### 2. Install Dependencies
```bash
pip install -r requirements_local.txt
```

### 3. Environment Configuration
1. Copy the `.env` file and update the following values:

```bash
# Required: Change this to a secure random string
SESSION_SECRET=your-unique-secret-key-here

# Optional: For contact form email functionality
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
```

### 4. Gmail Setup (Optional - for contact form)
To enable email functionality:

1. **Enable 2FA on your Google Account**
   - Go to Google Account Settings → Security
   - Turn on 2-Step Verification

2. **Generate App Password**
   - Go to Google Account Settings → Security → App passwords
   - Select "Mail" and your device
   - Copy the 16-character password
   - Use this as your `MAIL_PASSWORD` in `.env`

3. **Update .env file**
   ```
   MAIL_USERNAME=your-actual-email@gmail.com
   MAIL_PASSWORD=your-16-char-app-password
   ```

### 5. Run the Application

#### Option A: Using the local runner (Recommended)
```bash
python run_local.py
```

#### Option B: Using Flask directly
```bash
python app.py
```

#### Option C: Using Gunicorn (Production-like)
```bash
gunicorn --bind 127.0.0.1:5000 --reload app:app
```

### 6. Access the Website
Open your browser and go to: `http://localhost:5000`

## Chatbot Knowledge Base Indexing
Embeddings are cached to avoid hitting API quotas. They are NOT built automatically at startup.

1. Set your `GOOGLE_API_KEY` in `.env`.
2. Build (or rebuild) the index after changing `data.txt`:
   ```bash
   python build_index.py
   ```
3. Start the app (e.g.):
   ```bash
   python main.py
   ```
4. If the chatbot responds that the knowledge base is not indexed, run the build step above.

The cache lives in the `cache/` directory (`vector_store.pkl` + `index_meta.json`). Delete it to force a full rebuild.

## Project Structure
```
portfolio/
├── app.py                 # Main Flask application
├── run_local.py          # Local development runner
├── requirements_local.txt # Python dependencies
├── .env                  # Environment variables
├── templates/            # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── about.html
│   ├── education.html
│   ├── work.html
│   └── contact.html
└── static/
    ├── css/style.css     # Main stylesheet
    ├── js/script.js      # JavaScript functionality
    ├── images/           # SVG assets
    │   ├── profile.svg
    │   └── logo.svg
    └── resume/
        └── resume.pdf    # Downloadable resume
```

## Features
- ✅ Responsive design for all devices
- ✅ Animated hero section with typewriter effect
- ✅ Contact form with email integration
- ✅ Resume download functionality
- ✅ Professional project showcase
- ✅ Skills visualization with animated progress bars
- ✅ Modern CSS animations and effects

## Customization
1. **Personal Information**: Update content in HTML templates
2. **Styling**: Modify `static/css/style.css`
3. **Resume**: Replace `static/resume/resume.pdf` with your own
4. **Profile Image**: Replace `static/images/profile.svg`
5. **Projects**: Update project details in `templates/work.html`

## Troubleshooting

### Contact Form Not Working
- Ensure Gmail credentials are correctly set in `.env`
- Check that 2FA is enabled and you're using an App Password
- Contact form will show success messages even if email fails

### Port Already in Use
- Change the port in `run_local.py` from 5000 to another port (e.g., 8000)
- Or kill the process using port 5000: `lsof -ti:5000 | xargs kill -9`

### Missing Dependencies
```bash
pip install --upgrade pip
pip install -r requirements_local.txt
```

## Production Deployment
For production deployment, consider:
- Setting `FLASK_ENV=production` in `.env`
- Using a proper WSGI server like Gunicorn
- Setting up a reverse proxy (Nginx)
- Using environment-specific configuration
- Implementing proper logging and monitoring

## Support
If you encounter any issues, check the Flask and Python versions, and ensure all dependencies are properly installed.