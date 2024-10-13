
  // CSRF token setup
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken');

  // AJAX call to book a tutor
  function bookNow(tutorId, button) {
    $.ajax({
      url: '/book-tutor/',
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'  // Set content type to JSON
      },
      data: JSON.stringify({ tutor_id: tutorId }),  // Stringify the data
      success: function(response) {
        // Clear previous notifications
        const container = $(button).closest('.button-container');
        container.find(`#notification-${tutorId}`).hide();
        container.find(`#error-notification-${tutorId}`).hide();

        // Show appropriate notification
        if (response.success) {
          const successNotification = container.find(`#notification-${tutorId}`);
          successNotification.show().text(response.message); // Show message from server
          // Hide after 5 seconds
          setTimeout(() => {
            successNotification.fadeOut();
          }, 5000);
        } else {
          const errorNotification = container.find(`#error-notification-${tutorId}`);
          errorNotification.show();

          // Handle specific error messages
          if (response.error.includes('active booking')) {
            errorNotification.text('You have already booked this tutor.');
          } else if (response.error.includes('rebook')) {
            errorNotification.text('You cannot rebook this tutor for 7 days after rejection.');
          } else {
            errorNotification.text('Booking failed.');
          }

          // Hide after 5 seconds
          setTimeout(() => {
            errorNotification.fadeOut();
          }, 5000);
        }
      },
      error: function(xhr, status, error) {
        console.error('An error occurred:', error);
        const errorNotification = $(button).closest('.button-container').find(`#error-notification-${tutorId}`);
        errorNotification.show().text('An unexpected error occurred. Please try again.');
        // Hide after 5 seconds
        setTimeout(() => {
          errorNotification.fadeOut();
        }, 5000);
      }
    });
  }

  // Additional functions for enquiries, filtering, and managing bookings would go here


