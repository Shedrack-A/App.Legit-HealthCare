# Legit HealthCare Services Ltd - Web Application

This is the official web application for Legit HealthCare Services Ltd, designed to manage patient registration, medical tests, and results for corporate health screenings.

## Features

*   **User Authentication:** Secure user registration and login system.
*   **Theme Switching:** Toggle between light and dark modes.
*   **Multi-Company & Yearly Data:** Data isolation for different companies (DCP/DCT) and selection by screening year.
*   **Patient Management:** Register, view, edit, and delete patient records.
*   **Consultation Records:** A dedicated interface for doctors to record consultation notes.
*   **Test Result Entry:** Forms for entering results for 7 different medical tests (FBC, KFT, etc.), including calculated fields.
*   **Admin Control Panel:**
    *   Role-Based Access Control (RBAC) with permissions.
    *   User and Role management.
    *   Temporary Access Code generation and activation system.

## Setup

1.  **Clone the repository.**
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Initialize the database:**
    ```bash
    export FLASK_APP=run.py  # On Windows use `set FLASK_APP=run.py`
    flask db upgrade
    ```
5.  **Create initial admin user and permissions:**
    ```bash
    flask create-admin
    flask init-permissions
    ```
6.  **Run the application:**
    ```bash
    python run.py
    ```
The application will be available at `http://127.0.0.1:5000`. Default admin login is `admin` / `adminpass`.

## Configuration

### Changing the Logo
1. Log in as an Administrator.
2. Navigate to the "Control Panel" from the main navigation.
3. Click on the "Branding" button.
4. Use the file upload fields to select a new logo for the Light Theme and/or the Dark Theme.
5. Click "Save Logos". The new logo will appear immediately.

---

## Future Implementation (Awaiting Details)

The following pages are planned but require more information before implementation:

*   **Director Page (PAGE FOUR):** A page for the hospital director to review patient data and test results and make final comments.
*   **Patient Report Page (PAGE FIVE):** A page to generate and export a comprehensive patient report in PDF format.
