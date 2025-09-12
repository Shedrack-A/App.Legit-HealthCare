from app import db, login_manager
from flask_login import UserMixin
from app import bcrypt

# Association table for the many-to-many relationship between users and roles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

    def has_permission(self, perm_name):
        for role in self.roles:
            for perm in role.permissions:
                if perm.name == perm_name:
                    return True
        return False

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.phone_number}')"

# Association table for roles and permissions
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    permissions = db.relationship('Permission', secondary=role_permissions, backref=db.backref('roles', lazy='dynamic'))

    def __repr__(self):
        return f"Role('{self.name}')"

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"Permission('{self.name}')"

class TemporaryAccessCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expiry_time = db.Column(db.DateTime, nullable=False)
    is_single_use = db.Column(db.Boolean, default=True)
    times_used = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    permission = db.relationship('Permission')
    user = db.relationship('User')

    def __repr__(self):
        return f"<TempCode {self.code}>"

from datetime import datetime, UTC

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.String(50), nullable=False)
    patient_id = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    email_address = db.Column(db.String(120))
    race = db.Column(db.String(50), nullable=False)
    nationality = db.Column(db.String(50), nullable=False)
    date_registered = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    # For data isolation
    company = db.Column(db.String(10), nullable=False) # e.g., 'DCP' or 'DCT'
    screening_year = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint('staff_id', 'company', 'screening_year', name='_staff_company_year_uc'),
                      db.UniqueConstraint('patient_id', 'screening_year', name='_patient_year_uc'))

    def __repr__(self):
        return f"Patient('{self.first_name}', '{self.last_name}', '{self.staff_id}')"

class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, unique=True)

    luts = db.Column(db.String(50))
    chronic_cough = db.Column(db.String(50))
    chronic_chest_pain = db.Column(db.String(50))
    chest_infection = db.Column(db.String(50))
    heart_dx = db.Column(db.String(50))
    palor = db.Column(db.String(50))
    jaundice = db.Column(db.String(50))
    murmur = db.Column(db.String(50))
    chest = db.Column(db.String(50))
    psa = db.Column(db.String(50))
    psa_remark = db.Column(db.Text)
    fbs = db.Column(db.String(50))
    rbs = db.Column(db.String(50))
    fbs_rbs_remark = db.Column(db.String(50))
    urine_analysis = db.Column(db.String(100))
    ua_remark = db.Column(db.String(50))
    diabetes_mellitus = db.Column(db.String(100))
    hypertension = db.Column(db.String(100))
    bp = db.Column(db.String(50))
    pulse = db.Column(db.String(50))
    spo2 = db.Column(db.String(50))
    hs_1_and_2 = db.Column(db.String(50))
    breast_exam = db.Column(db.String(50))
    breast_exam_remark = db.Column(db.Text)
    abdomen = db.Column(db.String(50))
    assessment_hx_pe = db.Column(db.String(100))
    other_assessments = db.Column(db.Text)
    overall_lab_remark = db.Column(db.Text)
    other_remarks = db.Column(db.Text)
    overall_assessment = db.Column(db.Text)

    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    patient = db.relationship('Patient', backref=db.backref('consultation', lazy=True, uselist=False))

    def __repr__(self):
        return f"<Consultation for Patient ID: {self.patient_id}>"

# --- Test Result Models ---

class FullBloodCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, unique=True)
    hct = db.Column(db.String(50))
    wbc = db.Column(db.String(50))
    plt = db.Column(db.String(50))
    lymp_percent = db.Column(db.String(50))
    lymp = db.Column(db.String(50))
    gra_percent = db.Column(db.String(50))
    gra = db.Column(db.String(50))
    mid_percent = db.Column(db.String(50))
    mid = db.Column(db.String(50))
    rbc = db.Column(db.String(50))
    mcv = db.Column(db.String(50))
    mch = db.Column(db.String(50))
    mchc = db.Column(db.String(50))
    rdw = db.Column(db.String(50))
    pdw = db.Column(db.String(50))
    hgb = db.Column(db.String(50))
    fbc_remark = db.Column(db.Text)
    other_remarks = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    patient = db.relationship('Patient', backref=db.backref('full_blood_count', lazy=True, uselist=False))

class KidneyFunctionTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, unique=True)
    k = db.Column(db.Float)
    na = db.Column(db.Float)
    cl = db.Column(db.Float)
    ca = db.Column(db.Float)
    hco3 = db.Column(db.Float) # Calculated
    urea = db.Column(db.Float)
    cre = db.Column(db.Float)
    kft_remark = db.Column(db.Text)
    other_remarks = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    patient = db.relationship('Patient', backref=db.backref('kidney_function_test', lazy=True, uselist=False))

class LipidProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, unique=True)
    tcho = db.Column(db.Float)
    tg = db.Column(db.Float)
    hdl = db.Column(db.Float) # Calculated
    ldl = db.Column(db.Float) # Calculated
    lp_remark = db.Column(db.Text)
    other_remarks = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    patient = db.relationship('Patient', backref=db.backref('lipid_profile', lazy=True, uselist=False))

class LiverFunctionTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, unique=True)
    ast = db.Column(db.String(50))
    alt = db.Column(db.String(50))
    alp = db.Column(db.String(50))
    tb = db.Column(db.String(50))
    cb = db.Column(db.String(50))
    lft_remark = db.Column(db.Text)
    other_remarks = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    patient = db.relationship('Patient', backref=db.backref('liver_function_test', lazy=True, uselist=False))

class ECG(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, unique=True)
    ecg_result = db.Column(db.Text)
    remark = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    patient = db.relationship('Patient', backref=db.backref('ecg', lazy=True, uselist=False))

class Spirometry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, unique=True)
    spirometry_result = db.Column(db.Text)
    remark = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    patient = db.relationship('Patient', backref=db.backref('spirometry', lazy=True, uselist=False))

class Audiometry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, unique=True)
    audiometry_result = db.Column(db.Text)
    remark = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    patient = db.relationship('Patient', backref=db.backref('audiometry', lazy=True, uselist=False))
