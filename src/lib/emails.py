#! /usr/bin/env python
# -*- coding: utf-8 -*-

# jarr - A Web based news aggregator.
# Copyright (C) 2010-2016  Cédric Bonhomme - https://www.JARR-aggregator.org
#
# For more information : https://github.com/JARR-aggregator/JARR/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import conf

logger = logging.getLogger(__name__)


def send(to="", bcc="", subject="", plaintext=""):
    """
    Send an email.
    """
    # Create message container - the correct MIME type is multipart/alternative
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = conf.NOTIFICATION_EMAIL
    msg['To'] = to
    msg.attach(MIMEText(plaintext, 'plain', 'utf-8'))

    with smtplib.SMTP(host=conf.NOTIFICATION_HOST,
                      port=conf.NOTIFICATION_PORT) as smtp:
        smtp.ehlo()
        if conf.NOTIFICATION_STARTTLS:
            smtp.starttls()
        smtp.ehlo()
        smtp.login(conf.NOTIFICATION_USERNAME, conf.NOTIFICATION_PASSWORD)
        smtp.sendmail(conf.NOTIFICATION_EMAIL, [msg['To']], msg.as_string())
