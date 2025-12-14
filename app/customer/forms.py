from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SelectField, IntegerField, TextAreaField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange

class PrintJobForm(FlaskForm):
    # This might be used if we had dynamic sub-forms, but for simplicity 
    # we might just do a single file upload per "Job" or handle multi-upload differently.
    # The prompt asks for "multi-file upload" in /customer/order/new.
    # We can use a MultipleFileField if Flask-WTF supports it (depends on version) or just 'render_kw={"multiple": True}'
    pass

class NewOrderForm(FlaskForm):
    # Simplified approach: allow uploading multiple STLs at once. 
    # Logic in route: create one job per STL.
    stl_files = FileField('Upload STLs', 
                          validators=[FileRequired(), FileAllowed(['stl'], 'STL files only!')],
                          render_kw={'multiple': True})
    
    material_type = SelectField('Material', choices=[('PLA', 'PLA'), ('PETG', 'PETG'), ('ABS', 'ABS')], validators=[DataRequired()])
    color = SelectField('Color', choices=[('Black', 'Black'), ('White', 'White'), ('Grey', 'Grey'), ('Red', 'Red'), ('Blue', 'Blue')], validators=[DataRequired()])
    
    # Note: Quantity here would apply to ALL files if simpler UI, 
    # or we force user to upload 1 by 1. 
    # Let's assume global settings for the batch for the "One Click" experience, 
    # or allow editing after draft. 
    # "Customer creates order -> Order.status='new'"
    # We will apply these settings to all uploaded files.
    quantity = IntegerField('Quantity (per file)', default=1, validators=[NumberRange(min=1)])
    
    notes = TextAreaField('Special Instructions')
    submit = SubmitField('Submit Order')
