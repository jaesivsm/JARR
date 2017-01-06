#! /usr/bin/env python
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bootstrap import conf
from lib.utils import rfc_1123_utc

logger = logging.getLogger(__name__)


def send(to="", bcc="", subject="", plaintext=""):
    """
    Send an email.
    """
    # Create message container - the correct MIME type is multipart/alternative
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = conf.NOTIFICATION_EMAIL
    msg['Date'] = rfc_1123_utc()
    msg['To'] = to
    msg.attach(MIMEText(plaintext, 'plain', 'utf-8'))

    with smtplib.SMTP(host=conf.NOTIFICATION_HOST,
                      port=conf.NOTIFICATION_PORT) as smtp:
        smtp.ehlo()
        if conf.NOTIFICATION_STARTTLS:
            smtp.starttls()
        smtp.ehlo()
        smtp.login(conf.NOTIFICATION_EMAIL, conf.NOTIFICATION_PASSWORD)
        smtp.sendmail(conf.NOTIFICATION_EMAIL, [msg['To']], msg.as_string())
