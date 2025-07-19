import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from flask_mail import Mail, Message

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/education')
def education():
    return render_template('education.html')

@app.route('/work')
def work():
    return render_template('work.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        purpose = request.form.get('purpose')
        description = request.form.get('description')
        
        if not all([name, email, phone, purpose]):
            flash('Please fill in all required fields.', 'error')
            return render_template('contact.html')
        
        # Try to send email, but don't fail if email is not configured
        try:
            if os.environ.get('MAIL_USERNAME') and os.environ.get('MAIL_PASSWORD'):
                # Send email
                msg = Message(
                    subject=f'Portfolio Contact: {purpose}',
                    recipients=[os.environ.get('MAIL_USERNAME')],
                    body=f'''
New contact form submission:

Name: {name}
Email: {email}
Phone: {phone}
Purpose: {purpose}
Description: {description if description else 'No description provided'}

Please respond promptly to this inquiry.
                    '''
                )
                mail.send(msg)
                flash('Message sent successfully! Thank you for reaching out.', 'success')
            else:
                # Log the contact form submission instead
                app.logger.info(f'Contact form submission - Name: {name}, Email: {email}, Phone: {phone}, Purpose: {purpose}')
                flash('Thank you for your message! I have received your contact information and will get back to you soon.', 'success')
            
            return redirect(url_for('contact'))
            
        except Exception as e:
            app.logger.error(f'Error sending email: {str(e)}')
            # Still show success to user, but log the submission
            app.logger.info(f'Contact form submission (email failed) - Name: {name}, Email: {email}, Phone: {phone}, Purpose: {purpose}')
            flash('Thank you for your message! I have received your contact information and will get back to you soon.', 'success')
            return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/download-resume')
def download_resume():
    return send_from_directory('static/resume', 'resume.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
