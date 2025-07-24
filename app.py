from flask import Flask, render_template, request, redirect, url_for, flash
from email.message import EmailMessage
import smtplib

app = Flask(__name__)
app.secret_key = "mysecretkey"  

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sendemail/", methods=["POST"])
def sendemail():
    try:
        name = request.form["name"]
        subject = request.form["subject"]
        sender_email = request.form["email"]
        message = request.form["message"]

        
        your_email = "amitpal8429755927@gmail.com"
        your_password = "juch jlbf wnxi tanq"  

       
        msg = EmailMessage()
        msg["Subject"] = f"New Contact: {subject}"
        msg["From"] = your_email
        msg["To"] = your_email
        msg["Reply-To"] = sender_email
        msg.set_content(f"""
You've received a new message from your portfolio contact form:

Name: {name}
Email: {sender_email}
Subject: {subject}

Message:
{message}
""")

        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(your_email, your_password)
        server.send_message(msg)
        server.quit()

        flash("Email sent to your Gmail successfully!", "success")
    except Exception as e:
        print("Error sending email:", e)
        flash("Failed to send email.", "danger")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
