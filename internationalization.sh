#! /bin/sh

pybabel extract -F src/web/translations/babel.cfg -k gettext,lazy_gettext -o src/web/translations/messages.pot src/web/
pybabel update -l fr -d src/web/translations/ -i src/web/translations/messages.pot
poedit src/web/translations/fr/LC_MESSAGES/messages.po
pybabel compile -d src/web/translations/ --statistics
