from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class RegisterForm(FlaskForm):
    """
    Form for registering users
    """

    username = StringField(
        "Username", validators=[DataRequired(message="Username is required")]
    )
    password = PasswordField(
        "Password",
        validators=[
            Length(min=8, message="Password must be at least 8 characters"),
            DataRequired(message="Password is required"),
        ],
    )
    match_password = PasswordField(
        "Retype Password",
        validators=[
            EqualTo("password", message="Passwords must match"),
            DataRequired(message="Password confirmation is required"),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Email must be in 'example@email.com' format"),
        ],
    )
    secret_question = StringField(
        "Secret Question",
        validators=[
            DataRequired(message="Secret question is required"),
            Length(max=28, message="Secret question must be 28 characters at maximum"),
        ],
    )
    secret_answer = PasswordField(
        "Secret Answer", validators=[DataRequired(message="Secret answer is required")]
    )


class LoginForm(FlaskForm):
    """
    Form for loggin in user
    """

    username = StringField(
        "Username", validators=[DataRequired(message="Username is required")]
    )
    password = PasswordField(
        "Password",
        validators=[
            Length(min=8, message="Password must be at least 8 characters"),
            DataRequired(message="Password is required"),
        ],
    )


class UserEditForm(FlaskForm):
    """
    Form for editing user
    """

    username = StringField("Username", validators=[Optional()])
    email = StringField(
        "Email",
        validators=[
            Email(message="Email must be in 'example@example.com' format"),
            Optional(),
        ],
    )
    new_password = PasswordField(
        "New Password",
        validators=[
            Length(min=8, message="Password must be at least 8 characters"),
            Optional(),
        ],
    )
    retype_new_password = PasswordField(
        "Retype New Password",
        validators=[
            Length(min=8, message="Password must be at least 8 characters"),
            EqualTo("new_password", message="Passwords must match"),
            Optional(),
        ],
    )
    secret_question = StringField(
        "Secret Question", validators=[Length(max=28), Optional()]
    )
    secret_answer = StringField("Secret Answer", validators=[Optional()])
    current_password = PasswordField(
        "Enter Current Password To Confirm Changes",
        validators=[DataRequired(message="Current password is required")],
    )


class ForgotPassUsername(FlaskForm):
    """
    Form for resetting password, entering username
    """

    username = StringField(
        "Username", validators=[DataRequired(message="Username is required")]
    )


class ForgotPassAnswer(FlaskForm):
    """
    Form for resetting password, entering secret answer
    """

    secret_question = StringField("Secret Question")
    secret_answer = PasswordField(
        "Secret Answer", validators=[DataRequired(message="Secret Answer is required")]
    )


class PasswordReset(FlaskForm):
    """
    Form for entering new password
    """

    new_password = PasswordField(
        "New Password", validators=[Length(min=8, message="Password is required")]
    )
    retype_password = PasswordField(
        "Retype New Password",
        validators=[
            Length(min=8, message="Password Confirmation is required"),
            EqualTo("new_password", message="Passwords must match"),
        ],
    )
