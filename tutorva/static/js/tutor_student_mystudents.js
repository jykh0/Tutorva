$(document).ready(function() {
  let studentIdToRemove = null;
  $('.btn-remove').click(function() {
    studentIdToRemove = $(this).data('student-id');
    $('#confirmModal').modal('show');
  });
  $('#confirmRemove').click(function() {
    $.ajax({
      url: '{% url "tutorstudentmystudents" %}',
      method: 'POST',
      data: {
        student_id: studentIdToRemove,
        csrfmiddlewaretoken: '{{ csrf_token }}'
      },
      success: function(response) {
        $('#student-' + studentIdToRemove).remove();
        $('#confirmModal').modal('hide');
        showMessage('Student removed successfully.');
      }
    });
  });
});
function showMessage(message) {
  $('#messageBox').text(message).fadeIn();
  setTimeout(function() {
    $('#messageBox').fadeOut();
  }, 1000);
}
