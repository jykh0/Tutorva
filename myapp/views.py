from django.shortcuts import render,redirect, get_object_or_404
from .models import User, Student, Tutor, Admin, Enquiry, Booking
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.urls import reverse
import json

from . import views

def landingpage(request):
    return render(request, "landingpage.html")

def logout(request):
    request.session.flush()
    print("Logout triggered")
    return redirect('landingpage')

def log(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        admin = Admin.objects.filter(email=email).first()
        if admin and admin.password == password:
            request.session['user_id'] = admin.id
            request.session['user_type'] = 'admin'
            return redirect('adminhome')
        user = User.objects.filter(email=email).first()
        email_error = None
        password_error = None
        status_error = None
        if not user:
            email_error = 'Email not found.'
        elif not check_password(password, user.password):
            password_error = 'Incorrect password.'
        elif not user.is_active:
            status_error = 'Your account is inactive. Please contact support.'
        context = {
            'email_value': email,
        }
        if email_error:
            context['email_error'] = email_error
        if password_error:
            context['password_error'] = password_error
        if status_error:
            context['status_error'] = status_error
        if email_error or password_error or status_error:
            return render(request, 'loginpage.html', context)
        request.session['user_id'] = user.id
        request.session['user_type'] = user.user_type
        if user.user_type == 'student':
            return redirect('studenthome')
        elif user.user_type == 'tutor':
            return redirect('tutorhome')
    return render(request, 'loginpage.html')



def stortu(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('register_as')
        if password != confirm_password:
            return render(request, "registerationpages/studentortutor.html", {"error": "Passwords do not match."})
        hashed_password = make_password(password)
        user = User.objects.create(uname=username, email=email, password=hashed_password, user_type=user_type)
        request.session['user_id'] = user.id
        if user_type == 'student':
            return redirect('student_register')
        elif user_type == 'tutor':
            return redirect('tutor_register')
    return render(request, "registerationpages/studentortutor.html")


def studentreg(request):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('studentortutor')
        fullname = request.POST['fullname']
        gender = request.POST['gender']
        phone = request.POST['phone']
        level = request.POST['level']
        subject = request.POST['subject']
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        location_type = request.POST['location_type']
        user = User.objects.get(id=user_id)
        Student.objects.create(
            uid=user, fullname=fullname, gender=gender, phone=phone, level=level,
            subject=subject, street=street, city=city, state=state, pincode=pincode, location_type=location_type
        )
        return redirect('loginpage')
    return render(request, "registerationpages/Studentregisterpage.html")


def tutorreg(request):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('studentortutor')
        fullname = request.POST.get('fullname')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        qualifications = request.POST.get('qualifications')
        subjects_offered = request.POST.get('subject')
        level = request.POST.get('level')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        availability = request.POST.get('availability')
        location_type = request.POST.get('location-type')

        # Debugging output to check received data
        print("Received data:", fullname, gender, phone, qualifications, subjects_offered, level, street, city, state,
              pincode, availability, location_type)
        if not all([fullname, gender, phone, qualifications, subjects_offered, level, street, city, state, pincode,
                    availability, location_type]):
            return HttpResponse('All fields are required.', status=400)
        if Tutor.objects.filter(phone=phone).exists():
            return HttpResponse('Phone number already exists.', status=400)
        user = User.objects.get(id=user_id)
        Tutor.objects.create(
            uid=user, fullname=fullname, gender=gender, phone=phone,
            qualifications=qualifications, subjects_offered=subjects_offered,
            level=level, street=street, city=city, state=state,
            pincode=pincode, availability=availability, location_type=location_type
        )
        return redirect('loginpage')
    return render(request, "registerationpages/Tutorregisterpage.html")


def studenthomepage(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    if not user_id or user_type != 'student':
        return redirect('log')
    user = get_object_or_404(User, id=user_id)
    student = get_object_or_404(Student, uid=user_id)
    tutors = Tutor.objects.filter(subjects_offered__icontains=student.subject)
    if not tutors.exists():
        tutors = Tutor.objects.filter(city=student.city)
    if not tutors.exists():
        tutors = Tutor.objects.filter(state=student.state)
    tutors = tutors.distinct()[:9]
    current_tutors = Tutor.objects.filter(booking__student=student, booking__is_accepted=True).distinct()
    context = { 'user': user, 'student_fullname': student.fullname, 'tutors': tutors, 'current_tutors': current_tutors }
    return render(request, "student/studenthome.html", context)


def submit_enquiry(request):
    if request.method == "POST":
        student = get_object_or_404(Student, uid=request.session.get('user_id'))
        tutor_id = request.POST.get('tutor_id')
        message = request.POST.get('message')
        tutor = get_object_or_404(Tutor, id=tutor_id)
        Enquiry.objects.create(student=student, tutor=tutor, message=message)
        messages.success(request, "Your enquiry has been sent to the tutor.")
        return redirect('studenthome')
    return redirect('studenthome')


def book_tutor(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'error': 'User not logged in.'})
    student = get_object_or_404(Student, uid=user_id)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            tutor_id = data.get('tutor_id')
            tutor = get_object_or_404(Tutor, id=tutor_id)
            existing_booking = Booking.objects.filter(student=student, tutor=tutor, is_rejected=False).first()
            if existing_booking:
                return JsonResponse({'success': False, 'error': 'You have already booked this tutor.'})
            rejected_booking = Booking.objects.filter(student=student, tutor=tutor, is_rejected=True).first()
            if rejected_booking and not rejected_booking.can_rebook():
                return JsonResponse({'success': False, 'error': 'You cannot rebook this tutor for another 7 days.'})
            Booking.objects.create(student=student, tutor=tutor)
            return JsonResponse({'success': True, 'message': 'Booking request sent successfully.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def tutorhome(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    if not user_id or user_type != 'tutor':
        return redirect('log')
    user = get_object_or_404(User, id=user_id)
    tutor = get_object_or_404(Tutor, uid=user_id)
    context = { 'user': user, 'tutor_fullname': tutor.fullname, 'tutor_gender': tutor.gender, }
    return render(request, "tutor/tutorhome.html", context)


def adminhome(request):
    return render(request, "admin/admin_homepage.html")


def adminstudents(request):
    try:
        students = Student.objects.select_related('uid').all()
        search_query = request.GET.get('search', '')
        if search_query:
            students = students.filter(
                Q(fullname__icontains=search_query) |
                Q(uid__email__icontains=search_query) |
                Q(phone__icontains=search_query)
            ).distinct()
        if request.method == 'POST':
            student_id = request.POST.get('student_id')
            action = request.POST.get('action')
            user = get_object_or_404(User, id=student_id)
            user.is_active = action == 'activate'
            user.save()
            return JsonResponse({'success': True, 'new_status': user.is_active})
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            students_list = []
            for student in students:
                students_list.append({
                    'uid': {
                        'id': student.uid.id,
                        'email': student.uid.email
                    },
                    'fullname': student.fullname,
                    'gender': student.gender,
                    'phone': student.phone,
                    'street': student.street,
                    'city': student.city,
                    'state': student.state,
                    'is_active': student.uid.is_active,
                })
            return JsonResponse({'students': students_list})
        return render(request, 'admin/admin_students.html', {'students': students})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def admintutors(request):
    search_query = request.GET.get('search', '')
    if search_query:
        tutors = Tutor.objects.select_related('uid').filter(
            Q(fullname__icontains=search_query) |
            Q(uid__email__icontains=search_query) |
            Q(phone__icontains=search_query)
        ).distinct()
    else:
        tutors = Tutor.objects.select_related('uid').all()
    if request.method == 'POST':
        tutor_id = request.POST.get('tutor_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, id=tutor_id)
        user.is_active = (action == 'activate')
        user.save()
        return JsonResponse({'success': True, 'new_status': user.is_active})
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tutors_list = []
        for tutor in tutors:
            tutors_list.append({
                'fullname': tutor.fullname, 'email': tutor.uid.email, 'phone': tutor.phone, 'qualifications': tutor.qualifications,
                'street': tutor.street, 'city': tutor.city, 'state': tutor.state, 'is_active': tutor.uid.is_active,
                'uid': {
                    'id': tutor.uid.id,
                }
            })
        return JsonResponse({'tutors': tutors_list})
    return render(request, 'admin/admin_tutor.html', {'tutors': tutors})

def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            token = get_random_string(20)
            reset_link = request.build_absolute_uri(reverse('resetpassword', args=[token]))
            try:
                send_mail(
                    'Password Reset Request',
                    f'Click the link below to reset your password:\n\n{reset_link}',
                    'jayakrishnanps2025@mca.ajce.in',
                    [email],
                    fail_silently=False,
                )
                user.reset_token = token
                user.save()
                messages.success(request, 'Password reset link has been sent to your email.')
            except Exception as e:
                messages.error(request, f'Error sending email: {str(e)}')
        else:
            messages.error(request, 'No account found with that email.')
    return render(request, 'forgotpassword.html')

def resetpassword(request, token):
    user = User.objects.filter(reset_token=token).first()
    if not user:
        messages.error(request, 'Invalid or expired reset token.')
        return redirect('forgotpassword')
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'resetpassword.html', {'token': token})
        user.password = make_password(new_password)
        user.reset_token = None
        user.save()
        messages.success(request, 'Password reset successful. You can now log in.')
        return redirect('loginpage')
    return render(request, 'resetpassword.html', {'token': token})


def studenteditprofile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('log')
    student = get_object_or_404(Student, uid=user_id)
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        phone = request.POST.get('phone')
        level = request.POST.get('level')
        subject = request.POST.get('subject')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        location_type = request.POST.get('location_type')
        profile_picture = request.FILES.get('profile_picture')
        remove_pic = request.POST.get('remove_pic')
        student.fullname = fullname
        student.phone = phone
        student.level = level
        student.subject = subject
        student.street = street
        student.city = city
        student.state = state
        student.pincode = pincode
        student.location_type = location_type
        if profile_picture:
            student.profile_picture = profile_picture
        elif remove_pic == '1':
            student.profile_picture = 'profile_pics/default_profile.jpg'
        student.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('studenteditprofile')
    context = {'student': student}
    return render(request, "student/student_editprofile.html", context)


def tutoreditprofile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('log')

    tutor = get_object_or_404(Tutor, uid=user_id)

    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        phone = request.POST.get('phone')
        qualifications = request.POST.get('qualifications')
        subjects_offered = request.POST.get('subjects_offered')
        level = request.POST.get('level')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        availability = request.POST.get('availability')
        location_type = request.POST.get('location_type')
        profile_picture = request.FILES.get('profile_picture')

        # Update tutor fields
        tutor.fullname = fullname
        tutor.phone = phone
        tutor.qualifications = qualifications
        tutor.subjects_offered = subjects_offered
        tutor.level = level
        tutor.street = street
        tutor.city = city
        tutor.state = state
        tutor.pincode = pincode
        tutor.availability = availability
        tutor.location_type = location_type

        # Handle profile picture
        if profile_picture:
            tutor.profile_picture = profile_picture
        elif request.POST.get('remove_profile_picture') == 'yes':
            tutor.profile_picture = 'profile_pics/default_profile.jpg'  # Reset to default picture

        tutor.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('tutoreditprofile')

    context = {'tutor': tutor}
    return render(request, "tutor/tutor_editprofile.html", context)


def tutor_notifications(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('log')
    tutor = Tutor.objects.filter(uid__id=user_id).first()
    if not tutor:
        return redirect('log')
    enquiries = Enquiry.objects.filter(tutor=tutor, tutor_x=False)
    bookings = Booking.objects.filter(tutor=tutor, tutor_x=False, student_x=False)  # Added tutor_x filter
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')

        if booking_id and action in ['accept', 'decline']:
            try:
                booking = Booking.objects.get(id=booking_id, tutor=tutor)
                if action == 'accept':
                    booking.is_accepted = True
                elif action == 'decline':
                    booking.is_rejected = True
                booking.tutor_x = True
                booking.save()
                return JsonResponse({'success': True})
            except Booking.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Booking not found.'})
        enquiry_id = request.POST.get('enquiry_id')
        if enquiry_id:
            try:
                enquiry = Enquiry.objects.get(id=enquiry_id, tutor=tutor)
                enquiry.tutor_x = True
                enquiry.save()
                return JsonResponse({'success': True})
            except Enquiry.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Enquiry not found.'})
    return render(request, 'tutor/tutor_notifications.html', {'enquiries': enquiries, 'bookings': bookings})


def reply_enquiry(request):
    if request.method == 'POST':
        enquiry_id = request.POST.get('enquiry_id')
        response = request.POST.get('response')
        try:
            enquiry = Enquiry.objects.get(id=enquiry_id)
            enquiry.response = response
            enquiry.status = 'answered'
            enquiry.save()
            return JsonResponse({'success': True})
        except Enquiry.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Enquiry not found.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})


def studentnotifications(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    if not user_id or user_type != 'student':
        return redirect('log')
    student = get_object_or_404(Student, uid=user_id)

    if request.method == 'POST':
        enquiry_id = request.POST.get('enquiry_id')
        try:
            enquiry = Enquiry.objects.get(id=enquiry_id)
            enquiry.student_x = True
            enquiry.save()
            return JsonResponse({'success': True})
        except Enquiry.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Enquiry not found.'})
    enquiries = Enquiry.objects.filter(student=student, status='answered', student_x=False)
    bookings = Booking.objects.filter(student=student, student_x=False)  # Only show bookings where student_x is False

    context = {
        'enquiries': enquiries,
        'bookings': bookings,
    }
    return render(request, 'student/student_notifications.html', context)


def delete_booking_notification(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        try:
            booking = Booking.objects.get(id=booking_id)
            booking.student_x = True
            booking.save()
            return JsonResponse({'success': True})
        except Booking.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Booking not found.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})


def studentviewprofile(request):
    student_id = request.GET.get('id')
    if student_id:
        student = get_object_or_404(Student, id=student_id)
    else:
        user = request.user
        student = get_object_or_404(Student, uid=user)
    return render(request, 'student/student_viewprofile.html', {
        'student': student
    })

def tutorviewprofile(request):
    tutor_id = request.GET.get('id')
    if tutor_id:
        tutor = get_object_or_404(Tutor, id=tutor_id)
    else:
        user = request.user
        tutor = get_object_or_404(Tutor, uid=user)
    return render(request, 'tutor/tutor_viewprofile.html', { 'tutor': tutor })
