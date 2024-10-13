function deleteBookingNotification(bookingId) {
    // AJAX request to update the student_x status for the booking
    $.ajax({
        url: '/path/to/your/delete/booking/url/',  // Replace with your URL
        type: 'POST',
        data: {
            'booking_id': bookingId,
            'csrfmiddlewaretoken': '{{ csrf_token }}',  // Include CSRF token if necessary
        },
        success: function(response) {
            if (response.success) {
                // Fade out the booking notification
                $('#booking-' + bookingId).fadeOut();
            } else {
                alert('Error: ' + response.error);
            }
        }
    });
}
