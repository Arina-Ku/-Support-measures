from flask_wtf import FlaskForm
from sqlalchemy.testing.pickleable import User
from werkzeug.routing import ValidationError
from wtforms import StringField, PasswordField, SelectMultipleField, SubmitField, TextAreaField
from wtforms import HiddenField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from App.models.admin import Admin
from App.models.industry import Industry
from App.models.category import Category
from App.models.region import Region
from App.models.business_registration_form import BusinessRegistrationForm

class RegistrationForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Lastname', validators=[DataRequired(), Length(min=3, max=30)])
    login = StringField('Login', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=30)])
    confirm_password = StringField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_login(self, login):
        admin = Admin.query.filter_by(login=login.data).first()
        if admin:
            raise ValidationError('This login already exists')

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=30)])
    submit = SubmitField('Login')


class SupportMeasureForm(FlaskForm):
    name = StringField('Название меры поддержки', validators=[DataRequired()],
                       render_kw={"class": "form-control", "placeholder": "Введите название"})
    description = TextAreaField('Описание', validators=[DataRequired()],
                                render_kw={"class": "form-control", "rows": 3})
    condition = TextAreaField('Условия', validators=[DataRequired()],
                              render_kw={"class": "form-control", "rows": 3})
    sourceLink = StringField('Ссылка на источник', validators=[DataRequired()],
                             render_kw={"class": "form-control", "placeholder": "https://example.com"})
    implementationPeriod = StringField('Срок реализации', validators=[DataRequired()],
                                     render_kw={"class": "form-control"})

    submit = SubmitField('Добавить', render_kw={"class": "btn btn-success mt-3"})

    #industries = SelectMultipleField('Отрасли', choices=[], render_kw={"class": "form-control"})
    #regions = SelectMultipleField('Регионы', choices=[], render_kw={"class": "form-control"})
    #business_forms = SelectMultipleField('Формы регистрации', choices=[], render_kw={"class": "form-control"})
    #categories = SelectMultipleField('Категории', choices=[], render_kw={"class": "form-control"})

class FilterForm(FlaskForm):
    categories = SelectMultipleField(
        'Категории',
        choices=[],
        validators=[Optional()],  # Обратите внимание на скобки ()
        render_kw={
            "class": "form-control selectpicker",
            "multiple": "true",
            "data-live-search": "true",
            "title": "Выберите категории"
        }
    )

    industries = SelectMultipleField(
        'Отрасли',
        choices=[],
        validators=[Optional()],  # Обратите внимание на скобки ()
        render_kw={
            "class": "form-control selectpicker",
            "multiple": "true",
            "data-live-search": "true",
            "title": "Выберите отрасли"
        }
    )

    regions = SelectMultipleField(
        'Регионы',
        choices=[],
        validators=[Optional()],  # Обратите внимание на скобки ()
        render_kw={
            "class": "form-control selectpicker",
            "multiple": "true",
            "data-live-search": "true",
            "title": "Выберите регионы"
        }
    )

    business_forms = SelectMultipleField(
        'Формы бизнеса',
        choices=[],
        validators=[Optional()],  # Обратите внимание на скобки ()
        render_kw={
            "class": "form-control selectpicker",
            "multiple": "true",
            "data-live-search": "true",
            "title": "Выберите формы бизнеса"
        }
    )

    support_purpose = StringField(
        'Цель получения поддержки*',
        validators=[Optional(), DataRequired(message="Поле обязательно для ИИ-подбора")],
        render_kw={
            "class": "form-control",
            "placeholder": "Пример: развитие экспорта, закупка оборудования"
        }
    )

    project_description = TextAreaField(
        'Описание проекта*',
        validators=[Optional(), DataRequired(message="Поле обязательно для ИИ-подбора")],
        # Обратите внимание на скобки ()
        render_kw={
            "class": "form-control",
            "placeholder": "Опишите суть проекта, этапы реализации, потребности",
            "rows": 4
        }
    )

    use_ai = BooleanField(
        'Использовать ИИ-подбор',
        default=True,
        render_kw={"class": "form-check-input"}
    )

    submit = SubmitField('Подобрать меры', render_kw={"class": "btn btn-primary"})

    def validate(self, **kwargs):
        # Стандартная валидация
        if not super().validate():
            return False

        # Дополнительная проверка для ИИ-режима
        if self.use_ai.data:
            if not self.support_purpose.data:
                self.support_purpose.errors.append('Это поле обязательно для ИИ-режима')
                return False
            if not self.project_description.data:
                self.project_description.errors.append('Это поле обязательно для ИИ-режима')
                return False

        return True

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.categories.choices = [(c.idCategory, c.categoryName) for c in
                                   Category.query.order_by(Category.categoryName).all()]
        self.industries.choices = [(i.idIndustry, i.industryName) for i in
                                   Industry.query.order_by(Industry.industryName).all()]
        self.regions.choices = [(r.idRegion, r.regionName) for r in Region.query.order_by(Region.regionName).all()]
        self.business_forms.choices = [(b.idBRF, b.BRFName) for b in
                                       BusinessRegistrationForm.query.order_by(BusinessRegistrationForm.BRFName).all()]
