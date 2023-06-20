import base64
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import mimetypes
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

MY_ADDRESS = "financialsummaries@gmail.com"
TO_ADDRESS = "financialsummaries@gmail.com"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def create_message(sender, to, subject, html_file_path):
    """Create a message for an email.
    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      html_file_path: The path to the HTML file to be used as the body of the email.
    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    with open(html_file_path, 'r') as f:
        html_string = f.read()

    msg = MIMEText(html_string, 'html')  # 'html' to specify the MIME type.
    message.attach(msg)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    return {
        'raw': raw_message
    }


def send_message(service, user_id, message):
    """Send an email message.
    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message: Message to be sent.
    Returns:
      Sent Message.
    """
    try:
        message = (service.users().messages().send(
            userId=user_id, body=message).execute())
        print(f"Message Id: {message['id']}")
        return message
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    msg = create_message(
        MY_ADDRESS, TO_ADDRESS, "Financial Summaries Test", r"sec-edgar-filings\0000320193\10-Q\0001193125-10-162840\filing-details.html")
    send_message(service, 'me', msg)


if __name__ == '__main__':
    main()
