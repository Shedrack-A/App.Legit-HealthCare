from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FloatField
from wtforms.validators import Optional, DataRequired

class FullBloodCountForm(FlaskForm):
    hct = StringField('HCT')
    wbc = StringField('WBC')
    plt = StringField('PLT')
    lymp_percent = StringField('LYMP(%)')
    lymp = StringField('LYMP')
    gra_percent = StringField('GRA(%)')
    gra = StringField('GRA')
    mid_percent = StringField('MID(%)')
    mid = StringField('MID')
    rbc = StringField('RBC')
    mcv = StringField('MCV(fl)')
    mch = StringField('MCH(pg)')
    mchc = StringField('MCHC(g/dl)')
    rdw = StringField('RDW(%)')
    pdw = StringField('PDW (%)')
    hgb = StringField('HGB')
    fbc_remark = TextAreaField('FBC Remark', validators=[Optional()])
    other_remarks = TextAreaField('Other Remarks', validators=[Optional()])
    submit = SubmitField('Submit FBC Results')

class KidneyFunctionTestForm(FlaskForm):
    k = FloatField('K', validators=[DataRequired()])
    na = FloatField('NA', validators=[DataRequired()])
    cl = FloatField('CL', validators=[DataRequired()])
    ca = FloatField('CA', validators=[DataRequired()])
    urea = FloatField('UREA', validators=[DataRequired()])
    cre = FloatField('CRE', validators=[DataRequired()])
    kft_remark = TextAreaField('KFT Remark', validators=[Optional()])
    other_remarks = TextAreaField('Other Remarks', validators=[Optional()])
    submit = SubmitField('Submit KFT Results')

class LipidProfileForm(FlaskForm):
    tcho = FloatField('TCHO', validators=[DataRequired()])
    tg = FloatField('TG', validators=[DataRequired()])
    lp_remark = TextAreaField('LP Remark', validators=[Optional()])
    other_remarks = TextAreaField('Other Remarks', validators=[Optional()])
    submit = SubmitField('Submit Lipid Profile Results')

class LiverFunctionTestForm(FlaskForm):
    ast = StringField('AST')
    alt = StringField('ALT')
    alp = StringField('ALP')
    tb = StringField('TB')
    cb = StringField('CB')
    lft_remark = TextAreaField('LFT Remark', validators=[Optional()])
    other_remarks = TextAreaField('Other Remarks', validators=[Optional()])
    submit = SubmitField('Submit LFT Results')

class ECGForm(FlaskForm):
    ecg_result = TextAreaField('ECG Result', validators=[DataRequired()])
    remark = TextAreaField('Remark', validators=[Optional()])
    submit = SubmitField('Submit ECG Results')

class SpirometryForm(FlaskForm):
    spirometry_result = TextAreaField('Spirometry Result', validators=[DataRequired()])
    remark = TextAreaField('Remark', validators=[Optional()])
    submit = SubmitField('Submit Spirometry Results')

class AudiometryForm(FlaskForm):
    audiometry_result = TextAreaField('Audiometry Result', validators=[DataRequired()])
    remark = TextAreaField('Remark', validators=[Optional()])
    submit = SubmitField('Submit Audiometry Results')
