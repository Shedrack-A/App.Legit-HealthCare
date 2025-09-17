from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class DirectorReviewForm(FlaskForm):
    """
    Form for the Director to add their review and assessment.
    """
    director_remarks = TextAreaField('Director Remarks', validators=[DataRequired()])
    overall_assessment = TextAreaField('Overall Assessment', validators=[DataRequired()])
    submit = SubmitField('Submit Review')
