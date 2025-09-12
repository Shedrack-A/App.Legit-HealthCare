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
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme) {
        setTheme(savedTheme);
    } else if (prefersDark) {
        setTheme('dark');
    } else {
        setTheme('light');
    }

    // Patient Search
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
