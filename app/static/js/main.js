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

function showToast(message, category = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${category}`;
    toast.textContent = message;

    container.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    // Animate out and remove after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        toast.addEventListener('transitionend', () => toast.remove());
    }, 5000);
}

// Apply the saved theme on page load
document.addEventListener('DOMContentLoaded', () => {
    // --- Profile Dropdown ---
    const profileDropdown = document.querySelector('.profile-dropdown');
    if(profileDropdown) {
        const dropdownToggle = profileDropdown.querySelector('a');
        const dropdownContent = profileDropdown.querySelector('.profile-dropdown-content');

        dropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
        });

        // Close dropdown if clicking outside
        document.addEventListener('click', function(e) {
            if (!profileDropdown.contains(e.target)) {
                dropdownContent.style.display = 'none';
            }
        });
    }

    // --- Countdown Timer for Temp Code ---
    const countdownTimer = document.getElementById('countdown-timer');
    if (countdownTimer) {
        const expiryTime = new Date(countdownTimer.dataset.expiry).getTime();

        const interval = setInterval(function() {
            const now = new Date().getTime();
            const distance = expiryTime - now;

            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            countdownTimer.innerHTML = `${minutes}m ${seconds}s`;

            if (distance < 0) {
                clearInterval(interval);
                countdownTimer.innerHTML = "EXPIRED";
                // Optionally hide or remove the notification bar
                countdownTimer.closest('.sticky-notification').style.display = 'none';
            }
        }, 1000);
    }

    // --- Profile Dropdown ---
    const profileDropdown = document.querySelector('.profile-dropdown');
    if(profileDropdown) {
        const dropdownToggle = profileDropdown.querySelector('a');
        const dropdownContent = profileDropdown.querySelector('.profile-dropdown-content');

        dropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
        });

        // Close dropdown if clicking outside
        document.addEventListener('click', function(e) {
            if (!profileDropdown.contains(e.target)) {
                dropdownContent.style.display = 'none';
            }
        });
    }

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
