from jinja2 import Environment, FileSystemLoader
import os
from dotenv import load_dotenv
import brevo_python
from brevo_python.rest import ApiException

load_dotenv()

# Ensure that all necessary environment variables are set
configuration = brevo_python.Configuration()
configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')


api_instance = brevo_python.TransactionalEmailsApi(brevo_python.ApiClient(configuration))

def send_email(recipient, subject, html_content, recipient_name):
    subject = "from the Python SDK!"
    sender = {"name":"FUR & FURBLE","email":"support@furandfable.com"}
    replyTo = {"name":"FUR & FURBLE","email":"support@furandfable.com"}

    to = [{"email": recipient,"name": recipient_name}]
    send_smtp_email = brevo_python.SendSmtpEmail(to=to, reply_to=replyTo, html_content=html_content, sender=sender, subject=subject, headers=None)
    
    try:
        # Send a transactional email
        api_response = api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print("Error sending email:", e)

def render_template(template_name, **kwargs):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    return template.render(**kwargs)