#! /usr/bin/env python
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jarr.lib.utils import rfc_1123_utc

from jarr.bootstrap import conf

logger = logging.getLogger(__name__)


def send(to="", bcc="", subject="", plaintext=""):
    """Send an email."""
    # Create message container - the correct MIME type is multipart/alternative
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = conf.NOTIFICATION_EMAIL
    msg['Date'] = rfc_1123_utc()
    msg['To'] = to
    msg.attach(MIMEText(plaintext, 'plain', 'utf-8'))

    with smtplib.SMTP(host=conf.notification.host,
                      port=conf.notification.port) as smtp:
        smtp.ehlo()
        if conf.notification.starttls:
            smtp.starttls()
        smtp.ehlo()
        smtp.login(conf.notification.login, conf.notification.password)
        smtp.sendmail(conf.notification.email, [msg['To']], msg.as_string())
