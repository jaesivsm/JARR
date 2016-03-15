from flask import Blueprint, render_template, flash, redirect, url_for
from flask.ext.babel import gettext
from flask.ext.login import login_required, current_user

from web.forms import CategoryForm
from web.controllers import CategoryController

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')
category_bp = Blueprint('category', __name__, url_prefix='/category')


@category_bp.route('/create', methods=['POST'])
@category_bp.route('/edit/<int:category_id>', methods=['POST'])
@login_required
def process_form(category_id=None):
    form = CategoryForm()
    cat_contr = CategoryController(current_user.id)

    if not form.validate():
        return render_template('edit_category.html', form=form)
    existing_cats = list(cat_contr.read(name=form.name.data))
    if existing_cats and category_id is None:
        flash(gettext("Couldn't add category: already exists."), "warning")
        return redirect(url_for('home', at='c', ai=existing_cats[0].id))
    # Edit an existing category
    category_attr = {'name': form.name.data}

    if category_id is not None:
        cat_contr.update({'id': category_id}, category_attr)
        flash(gettext('Category %(cat_name)r successfully updated.',
                      cat_name=category_attr['name']), 'success')
        return redirect(url_for('home', at='c', ai=category_id))

    # Create a new category
    new_category = cat_contr.create(**category_attr)

    flash(gettext('Category %(category_name)r successfully created.',
                  category_name=new_category.name), 'success')

    return redirect(url_for('home', at='c', ai=new_category.id))
