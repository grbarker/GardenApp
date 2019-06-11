from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Plant, Garden, Post
from flask_login import current_user



#For fixing the duplicate username bug. Catches the duplicate before it can cause 500 internal server error.
#The duplicate username bug comes from the fact that the username field has the "unique" parameter set to true.
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username. Username taken.')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=500)])
    submit1 = SubmitField('Submit')


class PostReplyForm(FlaskForm):
    reply_post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=500)])
    parent_post_id = HiddenField(validators=[
        DataRequired()])
    submit3 = SubmitField('Reply')


class WallPostForm(FlaskForm):
    wall_post = TextAreaField('Post something ', validators=[
        DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Submit')


class PlantFormDropDown(FlaskForm):
    plant = StringField('What did you plant', validators=[
        DataRequired(), Length(min=1, max=140)])
    garden = SelectField('Gardens', coerce=int)
    submit2 = SubmitField('Submit')


class PlantFormFromGardenPage(FlaskForm):
    plant = StringField('What did you plant', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')



class GardenForm(FlaskForm):
    name = StringField("What's the name of this new garden?", validators=[DataRequired(), Length(min=1, max=140)])
    address = StringField("Please provide an address for this garden.", validators=[DataRequired(), Length(min=1, max=240)])
    submit = SubmitField('Submit')

    def validate_name(self, name):
        gardens = current_user.gardens
        for garden in gardens:
            if name.data == garden.name and self.address.data == garden.address:
                raise ValidationError('You already have a garden by this name at this location.')

class DeleteGardenForm(FlaskForm):
    submit = SubmitField('Delete')

