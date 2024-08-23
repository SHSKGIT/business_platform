from ..sqlalchemy_setup import get_dbsession
from ..models.email import Email

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import environ
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


def prepare_email(**kwarg):
    dbsession = next(get_dbsession())  # Get the SQLAlchemy session

    name = kwarg["name"]
    email = kwarg["email"]

    if kwarg["type"] == "contact":
        comment = kwarg["comment"]
        new_contact = kwarg["new_contact"]

        # Remove any leading/trailing whitespace from each line
        comment = "<br>".join(line.strip() for line in comment.split("\n"))

        body = f"""
                    <html>
                    <body>
                        <h2>Dear {name},</h2>
                        <p>Thank you for contacting us!</p>
                        <p>The following is your comment:</p>
                        <blockquote style="background-color: #f0f0f0; padding: 10px;">
                            {comment}
                        </blockquote>
                        <p>Best regards,<br>Yunxiao (Jerry) Wang</p>
                    </body>
                    </html>
                """
    elif kwarg["type"] == "subscribe":
        new_subscribe = kwarg["new_subscribe"]

        body = f"""
                    <html>
                    <body>
                        <h2>Dear {name},</h2>
                        <p>Thank you for subscribing our newsletter! We will email you once there is any news coming up!</p>
                        <p>Best regards,<br>Yunxiao (Jerry) Wang</p>
                    </body>
                    </html>
                """

    sender_email = env("SENDER_EMAIL_ADDRESS")
    sender_password = env(
        "SENDER_EMAIL_PASSWORD"
    )  # Use an app-specific password if 2FA is enabled
    recipient_email = email
    cc_email = sender_email  # a string, ex: 'hello@hotmail.com,hello@gmail.com'
    subject = f"Re: Notification from {kwarg['type']} form"

    is_sent = send_email(
        sender_email, sender_password, recipient_email, cc_email, subject, body
    )

    # Create a new email object
    new_email = Email(
        subject=subject,
        sender=sender_email,
        recipient=recipient_email,
        cc=cc_email,
        is_sent=is_sent,
        contact_id=(new_contact.id if kwarg["type"] == "contact" else None),
        subscribe_id=(new_subscribe.id if kwarg["type"] == "subscribe" else None),
    )

    # Add to session and commit, take effect to db table.
    dbsession.add(new_email)
    dbsession.commit()
    dbsession.refresh(new_email)


def send_email(sender_email, sender_password, recipient_email, cc_email, subject, body):
    try:
        # Create the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject

        # Add CC email addresses
        if cc_email:
            message["Cc"] = cc_email
            # Combine recipient and CC addresses
            all_recipients = [recipient_email] + cc_email.split(",")
        else:
            all_recipients = [recipient_email]

        # Add body to email
        message.attach(MIMEText(body, "html"))

        # Create SMTP session
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            # Start TLS for security
            server.starttls()

            # Login to the server
            server.login(sender_email, sender_password)

            # Send the email
            server.sendmail(sender_email, all_recipients, message.as_string())

        logger.info("Email sent successfully")
        return True
    except Exception as ex:
        logger.error(f"Email sent failed. An error occurred: {str(ex)}")
        return False
