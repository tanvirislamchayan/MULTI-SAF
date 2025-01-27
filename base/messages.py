#mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


def sendmail(recipient_name, message, subject, recipient_email, template_name, domain=None, context=None):
    try:
        # Load the email template and context
        if not context:
            context = {
                'username': recipient_name,
                'message': message,
                'domain': domain, 
            }

        email_body = render_to_string(f'public/base/{template_name}', context)

        # Create and send the email
        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email=settings.EMAIL_HOST_USER,
            to=recipient_email,  # Ensure this is a list
        )
        email.content_subtype = 'html' 
        email.send()
        print('Message sent')
    except Exception as e:
        print(f"Failed to send email: {str(e)}")