from flask_wtf import Form
from wtforms import StringField, DateField, IntegerField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class AddTaskForm(Form):
    task_id = IntegerField()
    name = StringField(label='Task Name', validators=[DataRequired()])
    due_date = DateField(label='Due_date(mm/dd/yyyy)', validators=[DataRequired('Please enter date in mm/dd/yyyy format')], format='%m/%d/%Y')
    priority = SelectField(label='Priority', validators=[DataRequired()], choices=[
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
        ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')
    ])
    status = IntegerField('Status')


class RegistrationForm(Form):
    name = StringField(label='Username', validators=[DataRequired(),
                                                     Length(min=6, max=25)])
    email = StringField(label='Email', validators=[DataRequired(),
                                                   Email(), Length(min=6, max=40)])
    password = PasswordField(label='Password', validators=[DataRequired(),
                                                           Length(min=6, max=40)])
    confirm = PasswordField(label='Confirm Password',
                            validators=[DataRequired(),
                                        EqualTo('password', message='Passwords must match')])


class LoginForm(Form):
    name = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
