from django.shortcuts import render,redirect, get_object_or_404
from .models import User, Student, Tutor, Admin
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.urls import reverse
from . import views

def landingpage(request):
    return render(request, "landingpage.html")


def log(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        admin = Admin.objects.filter(email=email).first()
        if admin and admin.password == password:
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
        if user.user_type == 'student':
            return redirect('studenthome')
        elif user.user_type == 'tutor':
            return redirect('tutor_home')
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
    if not user_id:
        return redirect('loginpage')
    student = Student.objects.filter(uid__id=user_id).first()
    if student:
        return render(request, "student_home.html", {"fullname": student.fullname})
    else:
        return redirect('loginpage')

def tutorhome(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('loginpage')
    tutor = Tutor.objects.filter(uid__id=user_id).first()
    if tutor:
        return render(request, "tutor_home.html", {"fullname": tutor.fullname})
    else:
        return redirect('loginpage')

def adminhome(request):
    return render(request, "admin/admin_homepage.html")


def adminstudents(request):
    students = Student.objects.select_related('uid').all()
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, id=student_id)
        if action == 'activate':
            user.is_active = True
        elif action == 'deactivate':
            user.is_active = False
        user.save()
        return JsonResponse({'success': True, 'new_status': user.is_active})
    return render(request, 'admin/admin_students.html', {'students': students})

def admintutors(request):
    tutors = Tutor.objects.select_related('uid').all()
    if request.method == 'POST':
        tutor_id = request.POST.get('tutor_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, id=tutor_id)
        if action == 'activate':
            user.is_active = True
        elif action == 'deactivate':
            user.is_active = False
        user.save()
        return JsonResponse({'success': True, 'new_status': user.is_active})
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

def studenthome_tutors(request):
    return render(request, "studenthome_tutors.html")