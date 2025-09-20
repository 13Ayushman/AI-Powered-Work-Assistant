import smtplib
from email.message import EmailMessage
from groq import Groq
from flask import Flask, request, render_template, jsonify

# Start Flask application
app = Flask(__name__)

# Initialize Groq client with your API key
client = Groq(api_key="Enter your Groq API key here")

@app.route("/")
def index():
    """Renders the main HTML page."""
    return render_template("index.html")

# Chatbot route
@app.route("/chat", methods=["POST"])
def get_bot_response():
    """Handles the chatbot functionality using the Groq API."""
    data = request.get_json()
    user_text = data.get('text', '')

    if not user_text:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = client.chat.completions.create(
            # Using a valid Groq model. The model 'openai/gpt-oss-20b' from your snippet is not a supported Groq model.
            model="openai/gpt-oss-20b", 
            messages=[
                {"role": "user", "content": user_text}
            ],
            temperature=1,
            max_completion_tokens=2048, # Increased to allow for longer responses
            top_p=1,
            stream=False # Keeping stream=False to ensure compatibility with your Flask setup
        )
        answer = response.choices[0].message.content
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Email sending route
@app.route("/send_email", methods=["POST"])
def send_email():
    """Handles sending an email via a web request."""
    data = request.get_json()
    recipient = data.get('recipient', '')
    subject = data.get('subject', '')
    body = data.get('body', '')

    if not all([recipient, subject, body]):
        return jsonify({"error": "Recipient, subject, and body are required."}), 400
    
    # --- EMAIL CONFIGURATION (IMPORTANT) ---
    # Replace these with your actual SMTP server details.
    # For security, use an app password from your email provider.
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "add you email"
    SENDER_PASSWORD = "add your app password"

    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        return jsonify({"message": "Email sent successfully!"})
    except Exception as e:
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

