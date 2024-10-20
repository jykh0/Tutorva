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


function bookNow(tutorId, button) {
  $.ajax({
    url: '/book-tutor/',
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken,
      'Content-Type': 'application/json'
    },
    data: JSON.stringify({ tutor_id: tutorId }),
    success: function(response) {
      const container = $(button).closest('.button-container');
      const successNotification = container.find(`#notification-${tutorId}`);
      const errorNotification = container.find(`#error-notification-${tutorId}`);
      successNotification.hide();
      errorNotification.hide();
      if (response.success) {
        successNotification.show().text(response.message || 'Booking request sent successfully!');
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
        setTimeout(() => {
          errorNotification.fadeOut();
        }, 5000);
      }
    },
    error: function(xhr, status, error) {
      console.error('An error occurred:', error);
      const errorNotification = $(button).closest('.button-container').find(`#error-notification-${tutorId}`);
      errorNotification.show().text('An unexpected error occurred. Please try again.');
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


function acceptBooking(bookingId) {
  fetch(window.location.href, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken,
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


function declineBooking(bookingId) {
  fetch(window.location.href, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken,
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


function deleteNotification(id) {
  fetch(window.location.href, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken,
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
        bookingRow.remove();
      }
    } else {
      console.error('Error:', data.error);
    }
  })
  .catch(error => console.error('Error:', error));
}

document.getElementById('searchInput').addEventListener('keyup', function() {
  const searchQuery = this.value.trim();
  fetch(`/sthome/?q=${encodeURIComponent(searchQuery)}`, {
    method: 'GET',
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(response => response.json())
  .then(data => {
    const tutorGrid = document.getElementById('tutorGrid');
    tutorGrid.innerHTML = '';
    if (data.tutors.length > 0) {
      data.tutors.forEach(tutor => {
        const tutorCard = `
          <div class="col-md-4 tutor-card" data-city="${tutor.city}" data-state="${tutor.state}">
            <div class="card">
              <center>
                <img src="${tutor.profile_picture}" alt="${tutor.fullname}" class="tutor-img rounded-circle">
              </center>
              <h5 class="tutor-name">${tutor.fullname}</h5>
              <p class="tutor-subject">${tutor.subjects_offered}</p>
              <div class="button-container">
                <button type="button" class="btn" onclick="bookNow(${tutor.id}, this)">Book Now</button>
                <div id="notification-${tutor.id}" style="display: none; background-color: green; color: white; border-radius: 5px; padding: 10px; margin-bottom: 15px;">
                  <br>Booking request sent successfully!
                </div>
                <div id="error-notification-${tutor.id}" style="display: none; background-color: orange; color: white; border-radius: 5px; padding: 10px; margin-bottom: 15px;">
                  <br>You have already booked this tutor.
                </div>
              </div>
              <div class="button-container">
                <button type="button" class="btn btn-enquiry" data-tutor-id="${tutor.id}" onclick="openEnquiryModal(${tutor.id}, '${tutor.fullname}')">Enquiry</button>
              </div>
            </div>
          </div>`;
        tutorGrid.innerHTML += tutorCard;
      });
    } else {
      const noTutorsMessage = '<div style="text-align: center; color: white; font-weight: bold; font-size: 25px;">Tutors not found</div>';
      tutorGrid.innerHTML = noTutorsMessage;
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
});
