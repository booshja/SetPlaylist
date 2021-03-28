from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, Length


class SearchForm(FlaskForm):
    """
    Form for searching bands
    """

    search = StringField("Search", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    """
    Form for registering users
    """

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=8)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    secret_question = StringField("Secret Question", validators=[DataRequired()])
    secret_answer = PasswordField("Secret Answer", validators=[DataRequired()])


class LoginForm(FlaskForm):
    """
    Form for loggin in user
    """

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class UserEditForm(FlaskForm):
    """
    Form for editing user
    """

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    new_password = PasswordField("New Password", validators=[Length(min=8)])
    retype_new_password = PasswordField(
        "Retype New Password", validators=[Length(min=8)]
    )
    secret_answer = StringField("Secret Answer", validators=[DataRequired()])
    current_password = PasswordField(
        "Enter Current Password To Confirm Changes", validators=[DataRequired()]
    )


class ForgotPassUsername(FlaskForm):
    """
    Form for resetting password, entering username
    """

    username = StringField("Username", validators=[DataRequired()])


class ForgotPassAnswer(FlaskForm):
    """
    Form for resetting password, entering secret answer
    """

    secret_question = StringField("Secret Question")
    secret_answer = PasswordField("Secret Answer", validators=[DataRequired()])


class PasswordReset(FlaskForm):
    """
    Form for entering new password
    """

    new_password = PasswordField("New Password", validators=[Length(min=8)])
    retype_password = PasswordField("Retype New Password", validators=[Length(min=8)])
