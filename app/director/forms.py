from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Optional

class DirectorReviewForm(FlaskForm):
    """
    Form for the Director to add or edit their review and assessment.
    """
    director_remarks = StringField('Director Remarks', validators=[Optional()])
    overall_assessment = StringField('Overall Assessment', validators=[Optional()])

    comment_one = StringField('Comment One', validators=[Optional()])
    comment_two = StringField('Comment Two', validators=[Optional()])
    comment_three = StringField('Comment Three', validators=[Optional()])
    comment_four = StringField('Comment Four', validators=[Optional()])

    submit = SubmitField('Save Review')
