from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, Length


class RecordForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=-1, max=200, message='Field should not have more than 200 characters.')])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=-1, max=200, message='Field should not have more than 200 characters.')])
    role = StringField('Employee Role', validators=[DataRequired(), Length(min=-1, max=200, message='Field should not have more than 100 characters.')])
    salary = StringField('Annual Salary (USD)', validators=[DataRequired(), Length(min=-1, max=200, message='Field should not have more than 200 characters.')])
    pdf = FileField('Scanned ID (PDF)')
    