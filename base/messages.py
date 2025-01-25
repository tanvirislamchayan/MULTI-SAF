#mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def sendmail(recipient_name, message, subject, recipient_email, template_name, domain=False):
    # Load the email template and context
    context = {
        'username': recipient_name,
        'message': message,
    }
    email_body = render_to_string(f'public/base/{template_name}', context)
    if domain:
        context.update({
            'domain': domain
        })
        email_body = render_to_string(f'public/base/{template_name}', context)


    # Create and send the email
    email = EmailMessage(
        subject=subject,
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=recipient_email, 
    )
    email.content_subtype = 'html' 
    email.send()
    print('message sent')

# Call the function
# send_custom_email()
# name = f'Tanvir Islam'
# message = f"We have successfully received your request! Your software will be ready within 1 to 2 hours. Our team will contact you shortly through email once it's completed. Thank you for choosing us!"
# subject = 'Welcome to JS Technology'
# recipient_email = 'titechbd135@gmail.com'
# template_name = 'congratulate.html'
# # sendmail(name, message, subject, recipient_email, template_name)
