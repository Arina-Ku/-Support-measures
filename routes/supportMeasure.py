from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from forms import SupportMeasureForm, FilterForm
from App.ai.recommender_service import recommender_service
from ..extenctions import db
from ..models.supportMeasures import SupportMeasure
from ..models.industry import Industry
from ..models.category import Category
from ..models.region import Region
from ..models.business_registration_form import BusinessRegistrationForm
from ..models.measure_industry import MeasureIndustry
from ..models.measure_brf import MeasureBRF
from ..models.measure_category import MeasureCategory
from ..models.measure_region import MeasureRegion



supportMeasure = Blueprint('supportMeasure', __name__)

if recommender_service is None:
    print("ИИ-рекомендации отключены (модель не загружена)")

@supportMeasure.route('/', methods=['POST', 'GET'])
def all():
    all_categories = Category.query.order_by(Category.categoryName).all()
    all_industries = Industry.query.order_by(Industry.industryName).all()
    all_regions = Region.query.order_by(Region.regionName).all()
    all_business_forms = BusinessRegistrationForm.query.order_by(BusinessRegistrationForm.BRFName).all()

    form = FilterForm()

    form.categories.choices = [(c.idCategory, c.categoryName) for c in all_categories]
    form.industries.choices = [(i.idIndustry, i.industryName) for i in all_industries]
    form.regions.choices = [(r.idRegion, r.regionName) for r in all_regions]
    form.business_forms.choices = [(bf.idBRF, bf.BRFName) for bf in all_business_forms]

    query = SupportMeasure.query
    ai_mode = False
    supports = []

    if request.method == "POST" and form.validate():
        use_ai = hasattr(form, 'use_ai') and form.use_ai.data and recommender_service

        if use_ai and (not form.support_purpose.data or not form.project_description.data):
            flash("Для ИИ-подбора необходимо заполнить оба текстовых поля", "warning")
            return render_template('supportMeasure/all.html',
                                   supports=query.distinct().all(),
                                   form=form,
                                   all_categories=all_categories,
                                   all_industries=all_industries,
                                   all_regions=all_regions,
                                   all_business_forms=all_business_forms)

        if form.categories.data:
            query = query.join(MeasureCategory).join(Category).filter(
                MeasureCategory.categoryID.in_(form.categories.data),
                MeasureCategory.measureID == SupportMeasure.idSupportMeasure
            )

        if form.industries.data:
            query = query.join(MeasureIndustry).join(Industry).filter(
                MeasureIndustry.industryID.in_(form.industries.data),
                MeasureIndustry.measureID == SupportMeasure.idSupportMeasure
            )

        if form.regions.data:
            query = query.join(MeasureRegion).join(Region).filter(
                MeasureRegion.regionID.in_(form.regions.data),
                MeasureRegion.measureID == SupportMeasure.idSupportMeasure
            )

        if form.business_forms.data:
            query = query.join(
                MeasureBRF,
                SupportMeasure.idSupportMeasure == MeasureBRF.measureID
            ).filter(
                MeasureBRF.brfID.in_(form.business_forms.data)
            )

        if use_ai:
            try:
                query_data = {
                    'categories': form.categories.data,
                    'regions': form.regions.data,
                    'business_forms': form.business_forms.data,
                    'support_purpose': form.support_purpose.data,
                    'project_description': form.project_description.data
                }
                supports = recommender_service.get_recommendations(query_data)
                ai_mode = True
            except Exception as e:
                flash(f"Ошибка ИИ-рекомендаций: {str(e)}", "danger")
    if not ai_mode:
        supports = query.distinct().all()

    return render_template('supportMeasure/all.html',
                           supports=supports,
                           form=form,
                           all_categories=all_categories,
                           all_industries=all_industries,
                           all_regions=all_regions,
                           all_business_forms=all_business_forms)

@supportMeasure.route('/supportMeasure/create', methods=['POST', 'GET'])
@login_required
def create():
    form = SupportMeasureForm()

    industries = Industry.query.order_by(Industry.industryName).all()
    regions = Region.query.order_by(Region.regionName).all()
    business_forms = BusinessRegistrationForm.query.order_by(BusinessRegistrationForm.BRFName).all()
    categories = Category.query.order_by(Category.categoryName).all()

    if request.method == 'POST':
        try:
            support_measure = SupportMeasure(
                name=request.form['name'],
                description=request.form['description'],
                condition=request.form['condition'],
                sourceLink=request.form['sourceLink'],
                implementationPeriod=request.form['implementationPeriod'],
                adminID=current_user.idAdmin
            )
            db.session.add(support_measure)
            db.session.flush()

            def add_relations(ids, relation_model, measure_field, id_field):
                for id in ids:
                    relation = relation_model(**{
                        measure_field: support_measure.idSupportMeasure,
                        id_field: id
                    })
                    db.session.add(relation)

            add_relations(request.form.getlist('industries'), MeasureIndustry, 'measureID', 'industryID')
            add_relations(request.form.getlist('regions'), MeasureRegion, 'measureID', 'regionID')
            add_relations(request.form.getlist('businessForms'), MeasureBRF, 'measureID', 'brfID')
            add_relations(request.form.getlist('categories'), MeasureCategory, 'measureID', 'categoryID')

            db.session.commit()
            flash('Мера поддержки успешно добавлена!', 'success')
            return redirect(url_for('supportMeasure.all'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при сохранении: {str(e)}', 'danger')

    return render_template('supportMeasure/create.html',
                           form=form,
                           industries=industries,
                           regions=regions,
                           business_forms=business_forms,
                           categories=categories)


@supportMeasure.route('/supportMeasure/<int:idSupportMeasure>/update', methods=['POST', 'GET'])
@login_required
def update(idSupportMeasure):
    support = SupportMeasure.query.get_or_404(idSupportMeasure)
    form = SupportMeasureForm(obj=support)

    industries = Industry.query.order_by(Industry.industryName).all()
    regions = Region.query.order_by(Region.regionName).all()
    business_forms = BusinessRegistrationForm.query.order_by(BusinessRegistrationForm.BRFName).all()
    categories = Category.query.order_by(Category.categoryName).all()

    current_industries = [mi.industryID for mi in support.industries]
    current_regions = [mr.regionID for mr in support.regions]
    current_business_forms = [mbf.brfID for mbf in support.brf]
    current_categories = [mc.categoryID for mc in support.categories]

    if form.validate_on_submit():
        try:
            form.populate_obj(support)

            new_industry_ids = [int(id) for id in request.form.getlist('industries')]
            new_region_ids = [int(id) for id in request.form.getlist('regions')]
            new_business_form_ids = [int(id) for id in request.form.getlist('businessForms')]
            new_category_ids = [int(id) for id in request.form.getlist('categories')]

            update_relations(support.industries, MeasureIndustry, 'industryID', current_industries, new_industry_ids,
                           support.idSupportMeasure)
            update_relations(support.regions, MeasureRegion, 'regionID', current_regions, new_region_ids,
                           support.idSupportMeasure)
            update_relations(support.brf, MeasureBRF, 'brfID', current_business_forms, new_business_form_ids,
                           support.idSupportMeasure)
            update_relations(support.categories, MeasureCategory, 'categoryID', current_categories, new_category_ids,
                           support.idSupportMeasure)

            db.session.commit()
            flash('Мера поддержки успешно обновлена', 'success')
            return redirect(url_for('supportMeasure.all'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении: {str(e)}', 'danger')

    return render_template('supportMeasure/update.html',
                         form=form,
                         support=support,
                         industries=industries,
                         regions=regions,
                         business_forms=business_forms,
                         categories=categories,
                         current_industries=current_industries,
                         current_regions=current_regions,
                         current_business_forms=current_business_forms,
                         current_categories=current_categories)


def update_relations(current_relations, relation_model, id_field, current_ids, new_ids, measure_id):
    for rel in current_relations:
        if getattr(rel, id_field) not in new_ids:
            db.session.delete(rel)

    for new_id in new_ids:
        if new_id not in current_ids:
            new_rel = relation_model()
            setattr(new_rel, id_field, new_id)
            new_rel.measureID = measure_id
            db.session.add(new_rel)

@supportMeasure.route('/supportMeasure/<int:idSupportMeasure>/delete', methods=['POST'])
@login_required
def delete(idSupportMeasure):
    support = SupportMeasure.query.get_or_404(idSupportMeasure)

    if request.method == 'POST':
        MeasureCategory.query.filter_by(measureID=idSupportMeasure).delete()
        MeasureRegion.query.filter_by(measureID=idSupportMeasure).delete()
        MeasureIndustry.query.filter_by(measureID=idSupportMeasure).delete()
        MeasureBRF.query.filter_by(measureID=idSupportMeasure).delete()

        db.session.delete(support)
        db.session.commit()
        flash('Мера поддержки успешно удалена', 'success')
        return redirect(url_for('supportMeasure.all'))


@supportMeasure.route('/supportMeasure/<int:idSupportMeasure>', methods=['GET'])
def details(idSupportMeasure):
    support = SupportMeasure.query.get_or_404(idSupportMeasure)
    return render_template('supportMeasure/details.html',
                         support=support)
