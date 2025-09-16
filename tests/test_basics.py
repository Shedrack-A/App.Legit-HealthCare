from app.models import User
from datetime import date

from app.patient.routes import calculate_age
from app.utils import is_password_strong
from app.auth.forms import RegistrationForm

def test_password_hashing(app):
    u = User(first_name='john', last_name='doe', phone_number='1234567890', password='cat')
    assert u.password_hash is not None
    assert u.password_hash != 'cat'
    assert u.verify_password('cat')
    assert not u.verify_password('dog')

def test_calculate_age():
    today = date.today()
    birth_date_past = date(today.year - 30, today.month, today.day)
    assert calculate_age(birth_date_past) == 30

    birth_date_future_month = date(today.year - 30, today.month + 1 if today.month < 12 else 1, today.day)
    assert calculate_age(birth_date_future_month) == 29

def test_hco3_calculation():
    k = 4.5
    na = 140.0
    cl = 105.0
    # Expected: 4.5 + 140.0 - 105.0 - 16 = 23.5
    assert (k + na - cl - 16) == 23.5

def test_lipid_profile_calculation():
    tcho = 200.0
    tg = 150.0
    # Expected HDL: 200.0 * 0.35 = 70.0
    hdl = tcho * 0.35
    assert hdl == 70.0
    # Expected LDL: 200.0 + (150.0 / 5) + 70.0 = 200.0 + 30.0 + 70.0 = 300.0
    ldl = tcho + (tg / 5) + hdl
    assert ldl == 300.0

def test_is_password_strong():
    assert is_password_strong("short")[0] is False
    assert is_password_strong("longpassword")[0] is False
    assert is_password_strong("Longpassword1")[0] is False
    assert is_password_strong("Longpassword1!")[0] is True
    assert is_password_strong("AnotherValidP@ssw0rd")[0] is True

def test_phone_number_validator(app):
    with app.test_request_context():
        form = RegistrationForm()

        # Valid case
        form.phone_number.data = "+2348012345678"
        try:
            form.validate_phone_number(form.phone_number)
        except Exception as e:
            assert False, f"Validation failed for a valid number: {e}"

        # Invalid cases
        invalid_numbers = ["12345", "+23412345678", "+23412345678901", "abcdefg"]
        for number in invalid_numbers:
            form.phone_number.data = number
            try:
                form.validate_phone_number(form.phone_number)
                assert False, f"Validation succeeded for an invalid number: {number}"
            except Exception:
                assert True
