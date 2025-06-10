// Common JavaScript functions for the patient module

// Initialize tooltips
$(function () {
    $('[data-bs-toggle="tooltip"]').tooltip()
});

// Handle AJAX form submissions
function handleAjaxForm(form, successCallback) {
    $(form).on('submit', function(e) {
        e.preventDefault();
        const formData = $(this).serialize();
        const url = $(this).attr('action');
        const method = $(this).attr('method');

        $.ajax({
            url: url,
            type: method,
            data: formData,
            success: function(response) {
                if (response.success) {
                    if (typeof successCallback === 'function') {
                        successCallback(response);
                    }
                } else {
                    // Handle form errors
                    alert(response.error || 'An error occurred');
                }
            },
            error: function(xhr, status, error) {
                alert('An error occurred: ' + error);
            }
        });
    });
}

// Datepicker initialization
function initDatePickers() {
    $('.datepicker').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        todayHighlight: true
    });
}

// Document ready
$(document).ready(function() {
    initDatePickers();
});

$('.doctor-carousel').owlCarousel({
    loop: true,
    margin: 20,
    nav: true,
    responsive: {
        0: {
            items: 1
        },
        768: {
            items: 2
        },
        992: {
            items: 3
        }
    }
});