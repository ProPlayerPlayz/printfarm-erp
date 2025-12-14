from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    # Customer Profile Fields
    phone = StringField('Phone', validators=[DataRequired(), Length(min=8, max=20)])
    address_line1 = StringField('Address Line 1', validators=[DataRequired(), Length(max=128)])
    address_line2 = StringField('Address Line 2', validators=[Length(max=128)])
    city = StringField('City', validators=[DataRequired(), Length(max=64)])
    state = StringField('State', validators=[DataRequired(), Length(max=64)])
    pincode = StringField('ZIP/Pincode', validators=[DataRequired(), Length(max=20)])
    country = StringField('Country', validators=[DataRequired(), Length(max=64)])
    
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')
