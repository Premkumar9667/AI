# Prem Kumar's AI Engineer Portfolio

## Overview

This is a professional portfolio website for Prem Kumar, an AI Engineer, built with Flask (Python) backend and HTML/CSS/JavaScript frontend. The website showcases his professional experience, education, skills, and provides a contact form with email functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **Styling**: Custom CSS with CSS variables for theming and responsive design
- **JavaScript**: Vanilla JavaScript for interactive features (mobile navigation, scroll animations, smooth scrolling)
- **UI Framework**: Custom CSS grid and flexbox layouts with modern design patterns
- **Icons**: Font Awesome 6.0 for social media and UI icons
- **Fonts**: Google Fonts (Inter) for typography

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Structure**: Simple MVC pattern with route handlers in `app.py`
- **Email Service**: Flask-Mail for contact form submissions via SMTP
- **Static Files**: Served through Flask's static file serving
- **Configuration**: Environment-based configuration using `os.environ`

## Key Components

### 1. Navigation System
- Fixed navigation bar with responsive mobile hamburger menu
- Active page highlighting
- Social media links (GitHub, LinkedIn, WhatsApp)
- Smooth scroll functionality

### 2. Page Structure
- **Home**: Hero section with typewriter animation, CTA buttons
- **About**: Personal story, achievements, resume preview/download
- **Education**: Timeline layout for academic background and skills visualization
- **Work**: Professional experience and project showcase with tech stacks
- **Contact**: Contact form with SMTP email integration

### 3. Interactive Features
- CSS animations (fade-in, typewriter effect, scroll animations)
- Mobile-responsive design with hamburger navigation
- Intersection Observer API for scroll-triggered animations
- Form validation and flash messaging

### 4. Email Integration
- Flask-Mail configuration for SMTP
- Contact form processing with validation
- Email notifications for form submissions

## Data Flow

1. **Static Content**: Templates render static portfolio content
2. **Contact Form**: 
   - User fills contact form → Flask validates input → Email sent via SMTP → Success/error message displayed
3. **Resume Download**: Static file serving for PDF resume
4. **Navigation**: Client-side routing through Flask URL routing

## External Dependencies

### Python Packages
- **Flask**: Web framework
- **Flask-Mail**: Email functionality
- **Logging**: Built-in Python logging

### Frontend Libraries
- **Font Awesome**: Icon library (CDN)
- **Google Fonts**: Typography (CDN)

### SMTP Configuration
- Gmail SMTP server (configurable)
- Environment variables for credentials:
  - `MAIL_USERNAME`
  - `MAIL_PASSWORD`
  - `MAIL_SERVER`
  - `MAIL_PORT`

## Deployment Strategy

### Environment Configuration
- Uses environment variables for sensitive configuration
- Default development settings with production overrides
- Session secret key management

### File Structure
```
/
├── app.py              # Main Flask application
├── main.py             # Application entry point
├── templates/          # Jinja2 HTML templates
│   ├── base.html       # Base template with navigation
│   ├── home.html       # Homepage
│   ├── about.html      # About page
│   ├── education.html  # Education & skills
│   ├── work.html       # Work experience
│   └── contact.html    # Contact form
└── static/
    ├── css/style.css   # Main stylesheet
    ├── js/script.js    # JavaScript functionality
    └── images/         # Static images and assets
```

### Completed Features (Latest Update - July 12, 2025)
1. **✅ Complete Contact Form**: Fully functional with email integration and fallback logging
2. **✅ All Static Assets**: 
   - Custom SVG profile image (`static/images/profile.svg`)
   - Custom SVG logo (`static/images/logo.svg`)
   - Professional PDF resume file (`static/resume/resume.pdf`)
3. **✅ Resume Download Route**: Fully implemented with proper file serving
4. **✅ All Template Files**: Complete and functional with animations
5. **✅ Email Functionality**: Contact form with SMTP integration and graceful fallback
6. **✅ Responsive Design**: Mobile-first approach with hamburger navigation
7. **✅ CSS Animations**: Typewriter effects, scroll animations, and interactive elements

### Replit-Specific Considerations
- Uses `host='0.0.0.0'` for Replit hosting compatibility
- Port 5000 configuration for development
- Environment variable support through Replit Secrets
- Debug mode enabled for development

### Recommended Next Steps
1. Complete the contact form email functionality
2. Add missing static assets (images, resume PDF)
3. Implement resume download route
4. Add proper error handling and logging
5. Complete truncated template content
6. Add input sanitization for contact form
7. Implement rate limiting for contact form submissions