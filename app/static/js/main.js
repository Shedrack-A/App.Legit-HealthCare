const themeSwitcher = document.getElementById('theme-switcher');
const html = document.documentElement;

// Function to set the theme
const setTheme = (theme) => {
    html.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
};

// Function to toggle the theme
const toggleTheme = () => {
    const currentTheme = html.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
};

// Event listener for the theme switcher button
if (themeSwitcher) {
    themeSwitcher.addEventListener('click', toggleTheme);
}

// Apply the saved theme on page load
document.addEventListener('DOMContentLoaded', () => {
    // --- Theme Management ---
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme) {
        setTheme(savedTheme);
    } else if (prefersDark) {
        setTheme('dark');
    } else {
        setTheme('light');
    }

    // --- General Form Submission Loading Indicator ---
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"], input[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Submitting...
                `;
            }
        });
    });

    // --- Select2 Initialization ---
    $('.select2-enable').select2({
        theme: "classic" // Using a theme that might blend better initially
    });

    // --- Mobile Navigation Toggle ---
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');

    if (mobileNavToggle && sidebar && sidebarOverlay) {
        mobileNavToggle.addEventListener('click', () => {
            sidebar.classList.toggle('is-open');
            sidebarOverlay.classList.toggle('is-active');
        });

        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('is-open');
            sidebarOverlay.classList.remove('is-active');
        });
    }

    // --- Patient Search ---
    const searchInput = document.getElementById('patient-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const staffId = this.value;
            if (staffId.length > 2) { // Start searching after a few characters
                fetch(`/patient/api/search?staff_id=${staffId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            // Optionally clear form or show 'not found' message
                        } else {
                            // Populate the form
                            document.querySelector('[name="staff_id"]').value = data.staff_id;
                            document.querySelector('[name="patient_id"]').value = data.patient_id;
                            document.querySelector('[name="first_name"]').value = data.first_name;
                            document.querySelector('[name="middle_name"]').value = data.middle_name || '';
                            document.querySelector('[name="last_name"]').value = data.last_name;
                            document.querySelector('[name="department"]').value = data.department;
                            document.querySelector('[name="gender"]').value = data.gender;
                            document.querySelector('[name="date_of_birth"]').value = data.date_of_birth;
                            document.querySelector('[name="contact_phone"]').value = data.contact_phone;
                            document.querySelector('[name="email_address"]').value = data.email_address || '';
                            document.querySelector('[name="race"]').value = data.race;
                            document.querySelector('[name="nationality"]').value = data.nationality;
                        }
                    })
                    .catch(error => console.error('Error:', error));
            }
        });
    }
});
