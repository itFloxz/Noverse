from django.core.mail import EmailMessage
from .models import User, OneTimePassword
from django.conf import settings
import random

# Function to generate a 6-digit OTP
def generate_otp():
    return ''.join(str(random.randint(1, 9)) for _ in range(6))

# Function to send OTP to the user's email
def send_code_to_user(email):
    try:
        # Retrieve user by email
        user = User.objects.get(email=email)
        
        # Generate OTP and create an entry in the OneTimePassword table
        otp_code = generate_otp()
        OneTimePassword.objects.create(user=user, code=otp_code)

        # Define email subject and content (HTML styled)
        subject = "One Time Password for Email Verification"
        current_site = "myAuth.com"
        email_body = f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; background-color: #f9f9f9;">
            <h2 style="color: #333; text-align: center;">OTP Verification</h2>
            <p style="color: #555; text-align: center;">Hi <strong>{user.first_name}</strong>,</p>
            <p style="color: #555; text-align: center;">Enter this OTP to verify your email:</p>
            <div style="font-size: 24px; font-weight: bold; color: #333; text-align: center; margin: 20px 0;">
                {otp_code}
            </div>
            <p style="color: #555; text-align: center;">If you didn't request this, please ignore.</p>
            <p style="color: #555; text-align: center;">Regards,<br>Noteverse Team</p>
        </div>
        '''

        # Send the email
        email_message = EmailMessage(
            subject=subject, 
            body=email_body, 
            from_email=settings.DEFAULT_FROM_EMAIL, 
            to=[email]
        )
        email_message.content_subtype = 'html'  # Ensure it's sent as an HTML email
        email_message.send(fail_silently=True)
        return True

    except User.DoesNotExist:
        print(f"User with email {email} does not exist.")
        return False

    except Exception as e:
        print(f"Failed to send OTP: {str(e)}")
        return False

# Function to send a normal email
def send_normal_email(data):
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()
