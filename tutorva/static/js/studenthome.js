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
      const successNotification = container.find(`#notification-${tutorId}`);
      const errorNotification = container.find(`#error-notification-${tutorId}`);

      // Hide any existing notifications
      successNotification.hide();
      errorNotification.hide();

      // Show appropriate notification
      if (response.success) {
        successNotification.show().text(response.message || 'Booking request sent successfully!');
        // Hide after 5 seconds
        setTimeout(() => {
          successNotification.fadeOut();
        }, 5000);
      } else {
        errorNotification.show();
        if (response.error.includes('active booking')) {
          errorNotification.text('You have already booked this tutor.');
        } else if (response.error.includes('rebook')) {
          errorNotification.text('You cannot rebook this tutor for 7 days after rejection.');
        } else {
          errorNotification.text(response.error || 'Booking failed.');
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

function openEnquiryModal(tutorId, tutorName) {
  $('#tutorId').val(tutorId);
  $('#tutorName').text(tutorName);
  $('#enquiryModal').modal('show');
}

function filterTutors() {
  const searchInput = document.getElementById('searchInput').value.toLowerCase();
  const tutorCards = document.querySelectorAll('.tutor-card');

  tutorCards.forEach(card => {
    const name = card.querySelector('.tutor-name').textContent.toLowerCase();
    const city = card.dataset.city.toLowerCase();
    const state = card.dataset.state.toLowerCase();

    if (name.includes(searchInput) || city.includes(searchInput) || state.includes(searchInput)) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
}

// Function to accept a booking
function acceptBooking(bookingId) {
  fetch(window.location.href, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken, // Include CSRF token
    },
    body: new URLSearchParams({
      'booking_id': bookingId,
      'action': 'accept'
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      const bookingRow = document.getElementById(`booking-${bookingId}`);
      bookingRow.innerHTML = `
        <span class="btn btn-success" style="border-radius: 20px; padding: 10px 20px;" disabled>Booking Accepted</span>
        <a href="#" class="btn-clear" style="background-color: orange; color: white; border-radius: 20px; padding: 10px 20px;" onclick="deleteNotification(${bookingId})">X</a>`;
    } else {
      console.error('Error:', data.error);
    }
  })
  .catch(error => console.error('Error:', error));
}

// Function to decline a booking
function declineBooking(bookingId) {
  fetch(window.location.href, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken, // Include CSRF token
    },
    body: new URLSearchParams({
      'booking_id': bookingId,
      'action': 'decline'
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      const bookingRow = document.getElementById(`booking-${bookingId}`);
      bookingRow.innerHTML = `
        <span class="btn btn-danger" style="border-radius: 20px; padding: 10px 20px;" disabled>Booking Declined</span>
        <a href="#" class="btn-clear" style="background-color: orange; color: white; border-radius: 20px; padding: 10px 20px;" onclick="deleteNotification(${bookingId})">X</a>`;
    } else {
      console.error('Error:', data.error);
    }
  })
  .catch(error => console.error('Error:', error));
}

// Function to delete a notification
function deleteNotification(id) {
  fetch(window.location.href, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken, // Include CSRF token
    },
    body: new URLSearchParams({
      'booking_id': id,
      'action': 'delete'
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      const bookingRow = document.getElementById(`booking-${id}`);
      if (bookingRow) {
        bookingRow.remove(); // Remove the booking row from the DOM
      }
    } else {
      console.error('Error:', data.error);
    }
  })
  .catch(error => console.error('Error:', error));
}
