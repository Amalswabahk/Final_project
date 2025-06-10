// Doctor-specific JavaScript

// Initialize prescription autocomplete
function initPrescriptionAutocomplete() {
    $('#id_medication').autocomplete({
        source: '/api/medications/',
        minLength: 2
    });
}

// Initialize patient search
function initPatientSearch() {
    $('#patient-search-input').on('input', function() {
        const query = $(this).val();
        if (query.length > 2) {
            $.get('/doctor/patients/search/', {q: query}, function(data) {
                $('#patient-search-results').html(data);
            });
        }
    });
}

// Document ready
$(document).ready(function() {
    initPrescriptionAutocomplete();
    initPatientSearch();
});