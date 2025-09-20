from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Optional

class DirectorReviewForm(FlaskForm):
    """
    Form for the Director to add or edit their review and assessment.
    """
    director_remarks = TextAreaField('Director Remarks', validators=[Optional()])
    overall_assessment = TextAreaField('Overall Assessment', validators=[Optional()])

    comment_one = TextAreaField('Comment One', validators=[Optional()])
    comment_two = TextAreaField('Comment Two', validators=[Optional()])
    comment_three = TextAreaField('Comment Three', validators=[Optional()])
    comment_four = TextAreaField('Comment Four', validators=[Optional()])

    submit = SubmitField('Save Review', render_kw={'class': 'btn btn-primary'})
