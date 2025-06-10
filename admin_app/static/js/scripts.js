// Admin-specific JavaScript

$(document).ready(function() {
    // Initialize select2 for permission selects
    $('.select2').select2({
        placeholder: "Select permissions",
        allowClear: true
    });

    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Toggle user active status
    $('.toggle-user-active').on('click', function(e) {
        e.preventDefault();
        const userId = $(this).data('user-id');
        const isActive = $(this).data('active') === 'True';
        const url = `/admin/users/${userId}/toggle-active/`;

        $.post(url, {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            is_active: !isActive
        }, function(data) {
            if (data.success) {
                location.reload();
            }
        });
    });
});

// Facility management functions
function initFacilityMap(facilityId, lat, lng) {
    // In a real implementation, this would initialize a map
    console.log(`Initializing map for facility ${facilityId} at ${lat}, ${lng}`);
}