// auth.js - Handles form toggling and role switching

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const signupForm = document.getElementById('signup-form');
    const loginForm = document.getElementById('login-form');
    const switchToLogin = document.getElementById('switch-to-login');
    const switchToSignup = document.getElementById('switch-to-signup');
    const formTitle = document.getElementById('form-title');
    const formSubtitle = document.getElementById('form-subtitle');
    // Role toggles
    const patientToggle = document.getElementById('patient-toggle');
    const practitionerToggle = document.getElementById('practitioner-toggle');
    const patientFields = document.getElementById('patient-fields');
    const practitionerFields = document.getElementById('practitioner-fields');
    // Login role toggles
    const loginPatientToggle = document.getElementById('login-patient-toggle');
    const loginPractitionerToggle = document.getElementById('login-practitioner-toggle');

    // Switch to Login
    switchToLogin.addEventListener('click', function(e) {
        e.preventDefault();
        signupForm.style.display = 'none';
        loginForm.style.display = 'block';
        formTitle.textContent = 'Login to AyurSutra';
        formSubtitle.textContent = 'Your personalized healing & therapy dashboard';
    });
    // Switch to Signup
    switchToSignup.addEventListener('click', function(e) {
        e.preventDefault();
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
        formTitle.textContent = 'Welcome to AyurSutra';
        formSubtitle.textContent = 'Holistic Panchakarma Patient & Practitioner Portal';
    });

    // Role toggle for signup
    patientToggle.addEventListener('click', function() {
        patientToggle.classList.add('active');
        practitionerToggle.classList.remove('active');
        patientFields.style.display = 'block';
        practitionerFields.style.display = 'none';
    });
    practitionerToggle.addEventListener('click', function() {
        practitionerToggle.classList.add('active');
        patientToggle.classList.remove('active');
        patientFields.style.display = 'none';
        practitionerFields.style.display = 'block';
    });

    // Role toggle for login
    loginPatientToggle.addEventListener('click', function() {
        loginPatientToggle.classList.add('active');
        loginPractitionerToggle.classList.remove('active');
    });
    loginPractitionerToggle.addEventListener('click', function() {
        loginPractitionerToggle.classList.add('active');
        loginPatientToggle.classList.remove('active');
    });

    // Leave form submission to the server so Django can process and redirect
});