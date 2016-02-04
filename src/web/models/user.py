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

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.4 $"
__date__ = "$Date: 2013/11/05 $"
__revision__ = "$Date: 2014/04/12 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import re
from datetime import datetime
from sqlalchemy.orm import validates
from flask.ext.login import UserMixin

from bootstrap import db


class User(db.Model, UserMixin):
    """
    Represent a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(), unique=True)
    password = db.Column(db.String())
    email = db.Column(db.String(254))

    is_admin = db.Column(db.Boolean(), default=False)
    is_api = db.Column(db.Boolean(), default=False)

    oauth_twitter = db.Column(db.String())
    oauth_facebook = db.Column(db.String())
    oauth_google = db.Column(db.String())

    date_created = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)
    feeds = db.relationship('Feed', backref='subscriber', lazy='dynamic',
                            cascade='all,delete-orphan')
    refresh_rate = db.Column(db.Integer, default=60)  # in minutes
    readability_key = db.Column(db.String(), default='')

    @validates('login')
    def validates_login(self, key, value):
        return re.sub('[^a-zA-Z0-9_\.]', '', value)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return '<User %r>' % (self.login)

    def dump(self):
        return {'id': self.id}
