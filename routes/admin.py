from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_login import login_user, logout_user
from forms import RegistrationForm, LoginForm
from ..extenctions import db, bcrypt
from ..models.admin import Admin

admin = Blueprint('admin', __name__)

@admin.route('/admin/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        admin = Admin(name=form.name.data, lastname=form.lastname.data, login=form.login.data, email=form.email.data, password=hashed_password, phone=form.phone.data, )
        try:
            db.session.add(admin)
            db.session.commit()
            flash(f"Registration {form.login.data} successful!", "success")
            return redirect(url_for('admin.login'))
        except Exception as e:
            print(str(e))
            flash("Registration failed!", "danger")
    return render_template('admin/registration.html', form=form)

@admin.route('/admin/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():  # Срабатывает только при POST
        admin = Admin.query.filter_by(login=form.login.data).first()
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            login_user(admin)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('supportMeasure.all'))
        else:
            flash('Неверный логин или пароль', 'danger')

    # GET-запрос или ошибка валидации
    return render_template('admin/login.html', form=form)

@admin.route('/admin/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('supportMeasure.all'))