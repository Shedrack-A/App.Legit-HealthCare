from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

class ConsultationForm(FlaskForm):
    luts = SelectField('LUTS', choices=[('No', 'No'), ('Yes', 'Yes')], validators=[DataRequired()])
    chronic_cough = SelectField('Chronic Cough', choices=[('No', 'No'), ('Yes', 'Yes')], validators=[DataRequired()])
    chronic_chest_pain = SelectField('Chronic Chest Pain', choices=[('No', 'No'), ('Yes', 'Yes')], validators=[DataRequired()])
    chest_infection = SelectField('Chest Infection', choices=[('No', 'No'), ('Yes', 'Yes')], validators=[DataRequired()])
    heart_dx = SelectField('Heart DX', choices=[('No', 'No'), ('Yes', 'Yes')], validators=[DataRequired()])
    palor = SelectField('Palor', choices=[('No', 'No'), ('Yes', 'Yes')], validators=[DataRequired()])
    jaundice = SelectField('Jaundice', choices=[('No', 'No'), ('Yes', 'Yes')], validators=[DataRequired()])
    murmur = SelectField('Murmur', choices=[('No', 'No'), ('Yes', 'Yes')], validators=[DataRequired()])
    chest = SelectField('Chest', choices=[('Clinically Clear', 'Clinically Clear'), ('Not Clear', 'Not Clear')], validators=[DataRequired()])
    psa = SelectField('Prostrate-Specific Antigen - PSA', choices=[('Negative', 'Negative'), ('Positive', 'Positive'), ('Not Applicable', 'Not Applicable')], validators=[DataRequired()])
    psa_remark = TextAreaField('PSA Remark', validators=[Optional()])
    fbs = StringField('FBS', default='Not Applicable', validators=[DataRequired()])
    rbs = StringField('RBS', default='Not Applicable', validators=[DataRequired()])
    fbs_rbs_remark = SelectField('FBS/RBS Remark', choices=[('Normal', 'Normal'), ('Abnormal', 'Abnormal'), ('Maybe Abnormal', 'Maybe Abnormal')], validators=[DataRequired()])
    urine_analysis = SelectField('Urine Analysis', choices=[
        ('No Abnormality', 'No Abnormality'),
        ('Proteinuria', 'Proteinuria'),
        ('Proteinuria+', 'Proteinuria+'),
        ('Proteinuria >+', 'Proteinuria >+'),
        ('Glucosuria', 'Glucosuria'),
        ('Glucosuria+', 'Glucosuria+'),
        ('Glucosuria >+', 'Glucosuria >+'),
        ('Proteinuria/Glucosuria', 'Proteinuria/Glucosuria')
    ], validators=[DataRequired()])
    ua_remark = SelectField('U/A Remark', choices=[('Normal', 'Normal'), ('Abnormal', 'Abnormal'), ('Maybe Abnormal', 'Maybe Abnormal')], validators=[DataRequired()])
    diabetes_mellitus = SelectField('Diabetes Mellitus - DM', choices=[
        ('No', 'No'),
        ('Yes - On Regular Medication', 'Yes - On Regular Medication'),
        ('Yes - Not on Regular Medication', 'Yes - Not on Regular Medication'),
        ('Yes - Not on Medication', 'Yes - Not on Medication')
    ], validators=[DataRequired()])
    hypertension = SelectField('Hypertension - HTM', choices=[
        ('No', 'No'),
        ('Yes - On Regular Medication', 'Yes - On Regular Medication'),
        ('Yes - Not on Regular Medication', 'Yes - Not on Regular Medication'),
        ('Yes - Not on Medication', 'Yes - Not on Medication')
    ], validators=[DataRequired()])
    bp = StringField('B.P', validators=[DataRequired()])
    pulse = StringField('PULSE - b/m', validators=[DataRequired()])
    spo2 = StringField('SPO2%', validators=[DataRequired()])
    hs_1_and_2 = SelectField('HS: 1&2', choices=[('Present', 'Present'), ('S3 Present', 'S3 Present'), ('S4 Present', 'S4 Present')], validators=[DataRequired()])
    breast_exam = SelectField('Breast Exam', choices=[('Not Applicable', 'Not Applicable'), ('Normal', 'Normal'), ('Abnormal', 'Abnormal')], validators=[DataRequired()])
    breast_exam_remark = TextAreaField('Breast Exam Remark', validators=[Optional()])
    abdomen = SelectField('Abdomen', choices=[('Normal', 'Normal'), ('Abnormal', 'Abnormal')], validators=[DataRequired()])
    assessment_hx_pe = SelectField('Assessment - HX/PE', choices=[
        ('Satisfactory', 'Satisfactory'),
        ('Elevated BP', 'Elevated BP'),
        ('Poorly Controled HTN', 'Poorly Controled HTN'),
        ('Known DM', 'Known DM'),
        ('Bladder Outlet Obstruction', 'Bladder Outlet Obstruction')
    ], validators=[DataRequired()])
    other_assessments = TextAreaField('Other Assessments', validators=[Optional()])
    overall_lab_remark = TextAreaField('Overall Lab Remark', validators=[Optional()])
    other_remarks = TextAreaField('Other Remarks', validators=[Optional()])
    overall_assessment = TextAreaField('Overall Assessment(s)', validators=[Optional()])
    submit = SubmitField('Submit Consultation')
