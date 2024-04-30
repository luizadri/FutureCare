from datetime import datetime 
from decimal import Decimal
import re
from django.db.models import Count
import random
from django.shortcuts import get_object_or_404, render,redirect
from django.core.mail import send_mail
from django.conf import settings
from App.models import CustomUser, Notification,Patients,Doctors,Departments,DoctorLeave,Appoinment
from django.contrib import messages
from django.contrib.auth.models import auth
from django.http import FileResponse
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth.decorators import login_required
# Create your views here.

def HomePage(request):

    return render(request, 'Home.html')

def LoginPage(request):

    return render(request, 'Login.html')

def RegisterPatientPage(request):

    return render(request, 'RegisterPatient.html')

def RegisterDoctorPage(request):

    departments = Departments.objects.all()
    return render(request, 'RegisterDoctor.html', {'departments':departments})

@login_required
def AdminHome(request):

    Susers = Departments.objects.all()
    Scount = Susers.count()
    Tusers = Doctors.objects.all()
    Tcount = Tusers.count()
    C = Patients.objects.all()
    Ccount = C.count()

    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()

    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()
    return render(request, 'admin/AdminHome.html',{'pending_users': pending_users, 'pending_count': pending_count, 'PendingBooking':PendingBooking, 'BookingCount':BookingCount , 'Scount':Scount , 'Tcount':Tcount , 'Ccount':Ccount})

@login_required
def DoctorHome(request):
    doct_id = request.user
    doctor = Doctors.objects.get(user_member = doct_id)
    PendingNotification = Notification.objects.filter(status = 'NEW',doctor = doctor)
    NotificationCount = PendingNotification.count()
    usr = Doctors.objects.get(user_member=request.user)
    current = request.user.id
    tcr = CustomUser.objects.get(id=current)
    ap = Appoinment.objects.filter(doctor=doctor,status='CONFIRMED')
    p = ap.count()
    return render(request, 'doctor/DoctorHome.html', {'usr':usr,'tcr':tcr ,'NotificationCount':NotificationCount, 'PendingNotification':PendingNotification, 'p':p })

@login_required
def PatientHome(request):

    current = request.user.id
    tcr = CustomUser.objects.get(id=current)
    usr = Patients.objects.get(user_member=request.user)
    ap = Appoinment.objects.filter(user_member=request.user,status='CONFIRMED')
    p = ap.count()

    return render(request, 'patient/PatientHome.html', {'usr':usr, 'tcr':tcr, 'p':p})

def PatientRegistration(request):
    if request.method == 'POST':
        firstname = request.POST.get('Fname')
        lastname = request.POST.get('Lname')
        usename = request.POST.get('Username')
        age = request.POST.get('Age')
        gender = request.POST.get('Gender')
        number = request.POST.get('Phone')
        email = request.POST.get('Email')
        image = request.FILES.get('Photo')
        type = '3'
        password = str(random.randint(100000,999999))
        if image == None:
                if gender == 'Male':
                    image = 'images/MaleUser.jpg'
                elif gender == 'Female':
                    image = 'images/FemaleUser.jpg'
                else:
                    image = 'images/OtherUser.jpg'
        if CustomUser.objects.filter(username=usename).exists(): 
            messages.error(request,'Username already exists, Try a new one')
            return redirect('RegisterPatientPage')
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request,'Email already exists, Try a new one')
            return redirect('RegisterPatientPage')
        
        elif Patients.objects.filter(number=number).exists():
            messages.error(request,'Phone Number already exists, Try a new one')
            return redirect('RegisterPatientPage')

        else:
            user = CustomUser.objects.create_user(username=usename,password=password,email=email,first_name=firstname,last_name=lastname,user_type=type,is_active=False)
            user.save()
            pat = Patients(age =age,gender = gender, number =number,image=image,user_member=user)
            pat.save()
            
            subject = 'Registration Confirmation'
            message = 'Registration is successfull ,Please wait for admin approval'
            send_mail(subject,"Hello " + usename +',\n'+ message ,settings.EMAIL_HOST_USER,{email})

            user1 = CustomUser.objects.get(is_superuser = 1)
            subject = 'New Patient Registration'
            message = 'You have a New Patient Registration Request ,Please check your profile for more information'
            send_mail(subject,"Hello " + user1.username +',\n'+ message ,settings.EMAIL_HOST_USER,{user1.email})
           
            messages.success(request, 'User registration successful. Please wait for admin approval.')
            return redirect('RegisterPatientPage')
    
    else:
        return redirect('RegisterPatientPage')
    
def DoctorRegistration(request):
    if request.method == 'POST':
        firstname = request.POST.get('Fname')
        lastname = request.POST.get('Lname')
        usename = request.POST.get('Username')
        age = request.POST.get('Age')
        gender = request.POST.get('Gender')
        number = request.POST.get('Phone')
        email = request.POST.get('Email')
        image = request.FILES.get('Photo')
        cv = request.FILES.get('cv')
        type = '2'
        password = str(random.randint(100000,999999))
        sel = request.POST.get('department')
        department_name = Departments.objects.get(id=sel)
        if image == None:
                if gender == 'Male':
                    image = 'images/MaleUser.jpg'
                elif gender == 'Female':
                    image = 'images/FemaleUser.jpg'
                else:
                    image = 'images/OtherUser.jpg'
        if CustomUser.objects.filter(username=usename).exists(): 
            messages.error(request,'Username already exists, Try a new one')
            return redirect('RegisterDoctorPage')
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request,'Email already exists, Try a new one')
            return redirect('RegisterDoctorPage')
        
        elif Patients.objects.filter(number=number).exists():
            messages.error(request,'Phone Number already exists, Try a new one')
            return redirect('RegisterDoctorPage')

        else:
            user = CustomUser.objects.create_user(username=usename,password=password,email=email,first_name=firstname,last_name=lastname,user_type=type,is_active=False)
            user.save()
            pat = Doctors(user_department = department_name,age =age,gender = gender, number =number,cv=cv,image=image,user_member=user)
            pat.save()
            
            subject = 'Registration Confirmation'
            message = 'Registration is successfull ,Please wait for admin approval'
            send_mail(subject,"Hello " + usename +',\n'+ message ,settings.EMAIL_HOST_USER,{email})

            user1 = CustomUser.objects.get(is_superuser = 1)
            subject = 'New Doctor Registration'
            message = 'You have a New Doctor Registration Request ,Please check your profile for more information'
            send_mail(subject,"Hello " + user1.username +',\n'+ message ,settings.EMAIL_HOST_USER,{user1.email})
           
            messages.success(request, 'User registration successful. Please wait for admin approval.')
            return redirect('RegisterDoctorPage')
    
    else:
        return redirect('RegisterDoctorPage')
    
def main_login(request):
    if request.method == 'POST':
        username = request.POST.get('Username')
        password = request.POST.get('Password')
        usr = auth.authenticate(request, username=username, password=password)
        if usr is not None:
            if usr.is_superuser:
                auth.login(request, usr)
                messages.success(request,'Welcome '+ usr.username)
                return redirect('AdminHome')
            elif usr.user_type == '3':
                auth.login(request, usr)
                # usr = Usermembers.objects.get(user_member=request.user)
                messages.success(request,'Welcome '+ usr.first_name + ' ' + usr.last_name)
                return redirect('PatientHome')
            else:
                auth.login(request, usr)
                messages.success(request,'Welcome '+ usr.first_name + ' ' + usr.last_name)
                return redirect('DoctorHome')
        else:
            messages.error(request,'Invalid Credentials')
            return redirect('LoginPage')
    else:
        return redirect('LoginPage')
    
@login_required
def approve_disapprove_users(request):
    pending_users = CustomUser.objects.filter(is_active=False)
    approved_users = CustomUser.objects.filter(is_active=True)
    pending_count = pending_users.count()

    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(CustomUser, id=user_id)
        user1 = get_object_or_404(CustomUser, id=user_id)
        

        if action == 'approve': 
            password = str(random.randint(100000, 999999))
            user.set_password(password)
            user.is_active = True
            user.save()

            usertype = user1.user_type

            if usertype == '2':
                subject = 'Registration Approved as Doctor'
                message = f"Hello {user.username},\n Your username is {user.username} and your password is {password} \n Your Doctor ID is {user_id}"
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            if usertype == '3':
                subject = 'Registration Approved'
                message = f"Hello {user.username},\n Your username is {user.username} and your password is {password} \n Your Patient ID is {user_id}"
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])


            messages.success(request, 'Approved')
            return redirect('approve_disapprove_users')

        elif action == 'disapprove':

            subject = 'Registration Disapproved'
            message = f"Hello {user.username},\n Your Registration Disapproved, Please Register again "
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            user.delete()
            

            messages.success(request, 'Disapproved')
            return redirect('approve_disapprove_users')

    return render(request, 'admin/Notification.html', {'pending_users': pending_users, 'pending_count': pending_count, 'approved_users': approved_users, 'PendingBooking':PendingBooking, 'BookingCount':BookingCount})

@login_required
def manage_department(request):
    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()

    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()

    dept = Departments.objects.all()
    doct = Doctors.objects.all()
    return render(request, 'admin/ViewDepartment.html',{'dept': dept , 'doct': doct ,'pending_count': pending_count, 'PendingBooking':PendingBooking, 'BookingCount':BookingCount})

@login_required
def edit_department(request, pk):
    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()

    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()

    dept = Departments.objects.get(id=pk)
    return render(request, 'admin/EditDepartment.html', {'dept': dept, 'pending_count': pending_count, 'PendingBooking':PendingBooking, 'BookingCount':BookingCount})

@login_required
def update_department(request, pk):
    if request.method == 'POST':
        dept = Departments.objects.get(id=pk)
        dept.department_name = request.POST.get('nme')

        dept.save()

        messages.success(request,'Department Updated successfully')

        return redirect('manage_department') 

    return render(request, 'admin/EditDepartment.html')

@login_required     
def add_department(request):
    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()
    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()
    return render(request,'admin/AddDepartment.html',{'pending_count': pending_count, 'PendingBooking':PendingBooking, 'BookingCount':BookingCount})

@login_required    
def reg_department(request):
    if request.method == 'POST':
        department_name = request.POST.get('acourse')
    
        dept = Departments(department_name = department_name)
        dept.save()
        messages.success(request,'Department added successfully')
        return redirect('manage_department')
    
@login_required
def view_cv(request, pk):
    doct = Doctors.objects.get(id=pk)
    return FileResponse(doct.cv, content_type='application/pdf')
    
@login_required
def doctor_details(request):

    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()
    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()
    doct = Doctors.objects.all()
    return render(request, 'admin/AllDoctors.html',{'doct': doct , 'pending_users':pending_users, 'pending_count': pending_count, 'PendingBooking':PendingBooking, 'BookingCount':BookingCount})

@login_required
def delete_doct(request,pk):
    
    doct = Doctors.objects.get(id=pk)
    crs = CustomUser.objects.get(username=doct.user_member.username)

    subject = 'Account Deleted'
    message = f"Hello {doct.user_member.username},\n Your Account has been deleted by the Admin"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [doct.user_member.email])

    doct.delete()
    crs.delete()
    messages.success(request,'Deleted Doctor successfully')
    return redirect('doctor_details')

def Doctor_Leave(request):
    doct_id = request.user
    doctor = Doctors.objects.get(user_member = doct_id)
    PendingNotification = Notification.objects.filter(status = 'NEW',doctor = doctor)
    NotificationCount = PendingNotification.count()
    current_doctor = request.user.id
    usr = Doctors.objects.get(user_member=request.user)
    if request.method == 'POST':
        date = request.POST.get('date')
        attendance_status = request.POST.get('attendance')
        attendance_record = DoctorLeave(doctor_name=usr, date=date, attendance=attendance_status)
        attendance_record.save()
        messages.success(request,'Leave Marked Successfully')

    return render(request, 'doctor/LeaveForm.html', {'usr':usr , 'PendingNotification':PendingNotification, 'NotificationCount':NotificationCount})

def BookAppoinment(request):

    usr = Patients.objects.get(user_member=request.user)
    dept = Departments.objects.all()
    return render(request, 'patient/BookAppoinment.html', {'usr':usr, 'dept':dept})

def ChooseDoctor(request):

    if request.method == "POST":
        pk = request.POST.get('dept')
        dept = Departments.objects.get(id = pk)
        usr = Patients.objects.get(user_member=request.user)
        doct = Doctors.objects.filter(user_department=pk)

        return render(request, 'patient/ChooseDoctor.html', {'usr':usr, 'doct':doct, 'dept':dept})

    else:
        return redirect('BookAppoinment')
    
def ConfirmBooking(request):
    if request.method == 'POST':
        user_id = request.user.id
        doctor_id = request.POST.get('doct')
        date = request.POST.get('date')
        description = request.POST.get('subject')

        try:
            # Check if the doctor is on leave
            doctor_on_leave = DoctorLeave.objects.get(doctor_name=doctor_id, date=date)
            messages.success(request, 'Doctor is on leave. Please choose another date.')
            return redirect('BookAppoinment')
        except DoctorLeave.DoesNotExist:
            pass  # Doctor is not on leave, proceed to check available slots

        # Check available slots
        available_slots = Appoinment.objects.filter(doctor=doctor_id, date=date).exclude(status__in=['PENDING', 'CANCELLED']).count()

        if available_slots >= 5:
            messages.success(request, 'Slot is full. Please choose another date or doctor.')
            return redirect('BookAppoinment')
        else:
            # Proceed with the booking
            doct = Doctors.objects.get(id=doctor_id)
            user_department = doct.user_department_id
            dept = Departments.objects.get(id=user_department)
            patient = Patients.objects.get(user_member=user_id)
            user = CustomUser.objects.get(id=user_id)

            appoinment = Appoinment(
                user_member=user,
                patient=patient,
                doctor=doct,
                department=dept,
                description=description,
                date=date
            )
            appoinment.save()

            messages.success(request, 'Booking successful. Please wait for confirmation.')
            return redirect('BookAppoinment')
    
def ApproveAppoinments(request):

    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()

    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    ApprovedBooking = Appoinment.objects.filter(status='CONFIRMED')
    BookingCount = PendingBooking.count()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        appointment_id = request.POST.get('appointment_id')
        action = request.POST.get('action')
        user = get_object_or_404(CustomUser, id=user_id)
        user1 = get_object_or_404(CustomUser, id=user_id)
        
        doct = Appoinment.objects.get(id=appointment_id)
        doctor = doct.doctor

        if action == 'CONFIRM': 
            appointment = Appoinment.objects.get(id=appointment_id)
            appointment.status = 'CONFIRMED'
            appointment.save()

            notification = Notification(doctor = doctor)
            notification.save()

            
            subject = 'Booking Confirmed'
            message = f"Hello {user.username},\n Your Booking is Confirmed"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            
            messages.success(request, 'Booking Confirmed')
            return redirect('ApproveAppoinments')

        elif action == 'CANCEL':

            appointment = Appoinment.objects.get(id=appointment_id)
            appointment.status = 'CANCELLED'
            appointment.save()
            subject = 'Booking Cancelled'
            message = f"Hello {user.username},\n Your Booking is Cancelled, Please Take a new Appoinment "
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            
            messages.success(request, 'Booking Cancelled')
            return redirect('ApproveAppoinments')

    return render(request, 'admin/Appoinments.html', {'pending_users': pending_users, 'pending_count': pending_count , 'PendingBooking':PendingBooking, 'ApprovedBooking':ApprovedBooking, 'BookingCount':BookingCount })

def ViewDoctorLeave(request):

    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()
    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()
    doct = Doctors.objects.all()
    return render(request, 'admin/ViewDoctorsLeave.html', {'doct':doct, 'pending_users':pending_users, 'pending_count':pending_count,'PendingBooking':PendingBooking, 'BookingCount':BookingCount })

def DoctorLeaveRecord(request):

    if request.method == 'POST':
        pending_users = CustomUser.objects.filter(is_active=False)
        pending_count = pending_users.count()
        PendingBooking = Appoinment.objects.filter(status = 'PENDING')
        BookingCount = PendingBooking.count()

        user_id = request.POST.get('sel')
        date = request.POST.get('date')

        try:
            doct = Doctors.objects.get(id=user_id)
            leave = DoctorLeave.objects.get(doctor_name=doct, date=date)
        except DoctorLeave.DoesNotExist:
            leave = None 

        return render(request, 'admin/LeaveRecord.html', {'leave':leave, 'date':date, 'doct':doct , 'pending_users':pending_users, 'pending_count':pending_count,'PendingBooking':PendingBooking, 'BookingCount':BookingCount  })
    
def ViewDoctorAppoinment(request):

    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()
    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()
    doct = Doctors.objects.all()
    return render(request, 'admin/ViewDoctorAppoinment.html', {'doct':doct, 'pending_users':pending_users, 'pending_count':pending_count,'PendingBooking':PendingBooking, 'BookingCount':BookingCount })

def DoctorAppoinmentRecord(request):

    if request.method == 'POST':
        pending_users = CustomUser.objects.filter(is_active=False)
        pending_count = pending_users.count()
        PendingBooking = Appoinment.objects.filter(status = 'PENDING')
        BookingCount = PendingBooking.count()

        user_id = request.POST.get('sel')
        date = request.POST.get('date')

        try:
            doct = Doctors.objects.get(id=user_id)
            appoinment = Appoinment.objects.filter(doctor=doct, date=date).exclude(status__in=['PENDING', 'CANCELLED'])
        except Appoinment.DoesNotExist:
            appoinment = None 

        return render(request, 'admin/DoctorAppoinmentRecord.html', {'appoinment':appoinment, 'date':date, 'doct':doct , 'pending_users':pending_users, 'pending_count':pending_count,'PendingBooking':PendingBooking, 'BookingCount':BookingCount  })
    
def PatientAppoinmentRecord(request):
        usr = Patients.objects.get(user_member=request.user)
        pending_users = CustomUser.objects.filter(is_active=False)
        pending_count = pending_users.count()
        PendingBooking = Appoinment.objects.filter(status = 'PENDING')
        BookingCount = PendingBooking.count()

        user_id = request.user

        try:
            appoinment = Appoinment.objects.filter(user_member=user_id).order_by('-id')
        except Appoinment.DoesNotExist:
            appoinment = None 

        return render(request, 'patient/viewAppoinments.html', {'usr':usr,'appoinment':appoinment, 'pending_users':pending_users, 'pending_count':pending_count,'PendingBooking':PendingBooking, 'BookingCount':BookingCount  })

def DoctorAppoinments(request):
    doct_id = request.user
    doctor = Doctors.objects.get(user_member = doct_id)
    PendingNotification = Notification.objects.filter(status = 'NEW',doctor = doctor)
    NotificationCount = PendingNotification.count()
    usr = Doctors.objects.get(user_member=request.user)
    return render(request, 'doctor/ViewAppoinment.html', {'usr':usr , 'PendingNotification':PendingNotification, 'NotificationCount':NotificationCount})

def DoctorAppoinmentsPage(request):
    doct_id = request.user
    doctor = Doctors.objects.get(user_member = doct_id)
    PendingNotification = Notification.objects.filter(status = 'NEW',doctor = doctor)
    NotificationCount = PendingNotification.count()
    if request.method == 'POST':
        usr = Doctors.objects.get(user_member=request.user)
        user_id = request.user
        date = request.POST.get('date')
        appointment_id = request.POST.get('appointment_id')
        action = request.POST.get('action')

        try:
            doct = Doctors.objects.get(user_member=user_id)
            appoinment = Appoinment.objects.filter(doctor=doct, date=date).exclude(status__in=['PENDING', 'CANCELLED'])
        except Appoinment.DoesNotExist:
            appoinment = None 

        if action == 'CONSULTED': 
            appointment = Appoinment.objects.get(id=appointment_id)
            appointment.status = 'CONSULTED'
            appointment.save()
            
            messages.success(request, 'Status Updated')
            return redirect('DoctorAppoinments')

        elif action == 'NOTCONSULTED':

            appointment = Appoinment.objects.get(id=appointment_id)
            appointment.status = 'NOT CONSULTED'
            appointment.save()
            
            messages.success(request, 'Status Updated')
            return redirect('DoctorAppoinments')

        return render(request, 'doctor/DoctorAppoinmentRecord.html', {'appoinment':appoinment, 'date':date, 'doct':doct , 'usr':usr , 'PendingNotification':PendingNotification, 'NotificationCount':NotificationCount })
    
def ViewPatientAppoinment(request):

    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()
    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()
    pat = Patients.objects.all()
    return render(request, 'admin/ViewPatientsAppoinment.html', {'pat':pat, 'pending_users':pending_users, 'pending_count':pending_count,'PendingBooking':PendingBooking, 'BookingCount':BookingCount })

def AppoinmentRecordPatient(request):

    if request.method == 'POST':
        pending_users = CustomUser.objects.filter(is_active=False)
        pending_count = pending_users.count()
        PendingBooking = Appoinment.objects.filter(status = 'PENDING')
        BookingCount = PendingBooking.count()

        user_id = request.POST.get('sel')
        date = request.POST.get('date')

        try:
            pat = Patients.objects.get(id=user_id)
            appoinment = Appoinment.objects.filter(patient=pat, date=date).order_by('-id')
        except Appoinment.DoesNotExist:
            appoinment = None 

        return render(request, 'admin/PatientAppoinmentRecord.html', {'appoinment':appoinment, 'date':date, 'pat':pat , 'pending_users':pending_users, 'pending_count':pending_count,'PendingBooking':PendingBooking, 'BookingCount':BookingCount  })
    
def DoctorPatientAppoinment(request):
    doct_id = request.user
    doctor = Doctors.objects.get(user_member = doct_id)
    PendingNotification = Notification.objects.filter(status = 'NEW',doctor = doctor)
    NotificationCount = PendingNotification.count()
    current_doctor = request.user
    doct = Doctors.objects.get(user_member=current_doctor)
    usr = Doctors.objects.get(user_member=request.user)
    appointments = Appoinment.objects.filter(doctor=doct).values('patient__user_member__id', 'patient__user_member__first_name', 'patient__user_member__last_name').annotate(num_appointments=Count('id'))
    patients = [{'id': app['patient__user_member__id'], 'name': f"{app['patient__user_member__first_name']} {app['patient__user_member__last_name']}", 'num_appointments': app['num_appointments']} for app in appointments]
    return render(request, 'doctor/ViewPatientAppoinment.html', {'patients': patients, 'usr': usr, 'PendingNotification':PendingNotification, 'NotificationCount':NotificationCount})

def DoctorPatientRecord(request):
    doct_id = request.user
    doctor = Doctors.objects.get(user_member = doct_id)
    PendingNotification = Notification.objects.filter(status = 'NEW',doctor = doctor)
    NotificationCount = PendingNotification.count()
    if request.method == 'POST':
        usr = Doctors.objects.get(user_member=request.user)

        user_id = request.POST.get('sel')

        try:
            pat = Patients.objects.get(user_member=user_id)
            appoinment = Appoinment.objects.filter(patient=pat).exclude(status__in=['PENDING', 'CANCELLED']).order_by('-id')
        except Appoinment.DoesNotExist:
            appoinment = None 

        return render(request, 'doctor/PatientAppoinmentRecord.html', {'usr': usr,'appoinment':appoinment, 'pat':pat, 'PendingNotification':PendingNotification, 'NotificationCount':NotificationCount  })

def AdminPatientAppoinment(request):
    
    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()

    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()
    
    appointments = Appoinment.objects.all().values('patient__user_member__id', 'patient__user_member__first_name', 'patient__user_member__last_name').annotate(num_appointments=Count('id'))
    patients = [{'id': app['patient__user_member__id'], 'name': f"{app['patient__user_member__first_name']} {app['patient__user_member__last_name']}", 'num_appointments': app['num_appointments']} for app in appointments]
    return render(request, 'admin/ViewAllPatientAppoinment.html', {'patients': patients, 'pending_users':pending_users, 'pending_count':pending_count,'PendingBooking':PendingBooking, 'BookingCount':BookingCount})

def AdminPatientRecord(request):

    if request.method == 'POST':
        pending_users = CustomUser.objects.filter(is_active=False)
        pending_count = pending_users.count()

        PendingBooking = Appoinment.objects.filter(status = 'PENDING')
        BookingCount = PendingBooking.count()

        user_id = request.POST.get('sel')

        try:
            pat = Patients.objects.get(user_member=user_id)
            appoinment = Appoinment.objects.filter(patient=pat).order_by('-id')
        except Appoinment.DoesNotExist:
            appoinment = None 

        return render(request, 'admin/AllPatientAppoinmentRecord.html', {'appoinment':appoinment, 'pat':pat, 'pending_users':pending_users, 'pending_count':pending_count,'PendingBooking':PendingBooking, 'BookingCount':BookingCount  })
    
def AllAppoinmentRecordPatient(request):

        doct_id = request.user
        doctor = Doctors.objects.get(user_member = doct_id)
        PendingNotification = Notification.objects.filter(status = 'NEW',doctor = doctor)
        NotificationCount = PendingNotification.count()
        usr = Doctors.objects.get(user_member=request.user)
        current_doctor = request.user
        doct = Doctors.objects.get(user_member=current_doctor)


        try:
            appoinment = Appoinment.objects.filter(doctor=doct).exclude(status__in=['PENDING', 'CANCELLED']).order_by('-id')
        except Appoinment.DoesNotExist:
            appoinment = None 

        return render(request, 'doctor/AllAppoinments.html', {'appoinment':appoinment , 'usr':usr, 'PendingNotification':PendingNotification, 'NotificationCount':NotificationCount })

def Notifications(request):

    doct_id = request.user
    doctor = Doctors.objects.get(user_member = doct_id)
    PendingNotification = Notification.objects.filter(status = 'NEW',doctor = doctor)
    NotificationCount = PendingNotification.count()

    usr = Doctors.objects.get(user_member=request.user)

    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        action = request.POST.get('action')
        notify = Notification.objects.get(id=appointment_id)

        if action == 'READ': 
            notify = Notification.objects.get(id=appointment_id)
            notify.status = 'OLD'
            notify.delete()
            messages.success(request, 'Notification SEEN')
            return redirect('Notifications')

    return render(request, 'doctor/Notification.html', {'usr':usr, 'NotificationCount':NotificationCount, 'PendingNotification':PendingNotification })

@login_required
def patient_details(request):

    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()
    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()
    doct = Patients.objects.all()
    return render(request, 'admin/AllPatients.html',{'doct': doct , 'pending_users':pending_users, 'pending_count': pending_count, 'PendingBooking':PendingBooking, 'BookingCount':BookingCount})

@login_required
def delete_pat(request,pk):
    
    doct = Patients.objects.get(id=pk)
    crs = CustomUser.objects.get(username=doct.user_member.username)

    subject = 'Account Deleted'
    message = f"Hello {doct.user_member.username},\n Your Account has been deleted by the Admin"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [doct.user_member.email])

    doct.delete()
    crs.delete()
    messages.success(request,'Deleted Patient successfully')
    return redirect('patient_details')

def logout(request):
    auth.logout(request)
    return redirect('LoginPage')


@login_required
def edit_doctor_profile(request):

    doct_id = request.user
    doctor = Doctors.objects.get(user_member = doct_id)
    PendingNotification = Notification.objects.filter(status = 'NEW',doctor = doctor)
    NotificationCount = PendingNotification.count()
    current_doctor = request.user.id
    tcr = CustomUser.objects.get(id=current_doctor)
    usr = Doctors.objects.get(user_member=request.user)
    return render(request,'doctor/EditProfile.html', {'tcr':tcr,'usr':usr, 'NotificationCount':NotificationCount, 'PendingNotification':PendingNotification })

@login_required
def edit_patient_profile(request):

    PendingNotification = Notification.objects.filter(status = 'NEW')
    NotificationCount = PendingNotification.count()
    current_doctor = request.user.id
    tcr = CustomUser.objects.get(id=current_doctor)
    usr = Patients.objects.get(user_member=request.user)
    return render(request,'patient/EditProfile.html', {'tcr':tcr,'usr':usr, 'NotificationCount':NotificationCount, 'PendingNotification':PendingNotification })


@login_required
def update_doctor_profile(request):
    if request.method == 'POST':
        current_doctor = Doctors.objects.get(user_member=request.user)
        current_user = current_doctor.user_member

        current_user.first_name = request.POST.get('fname')
        current_user.last_name = request.POST.get('lname')
        
        email = request.POST.get('mail')
        old_email = current_user.email

        if old_email != email:
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email ID already taken! Try a different one')
                return redirect('edit_doctor_profile')
            else:
                current_user.email = email

        number = request.POST.get('num')
        old_number = current_doctor.number

        if old_number != number:
            if number and Doctors.objects.exclude(id=current_doctor.id).filter(number=number).exists():
                messages.error(request, 'Number already exists! Try a different one')
                return redirect('edit_doctor_profile')
            else:
                current_doctor.number = number

        current_doctor.age = request.POST.get('age')
        remove_photo = request.POST.get('remove')

        if request.FILES.get('img'):
            current_doctor.image = request.FILES['img']

        if remove_photo == 'True':
            current_doctor.image = 'images/OtherUser.jpg'

        current_user.save()
        current_doctor.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('DoctorHome')

    return redirect('edit_doctor_profile')

@login_required
def update_patient_profile(request):
    if request.method == 'POST':
        current_doctor = Patients.objects.get(user_member=request.user)
        current_user = current_doctor.user_member

        current_user.first_name = request.POST.get('fname')
        current_user.last_name = request.POST.get('lname')
        
        email = request.POST.get('mail')
        old_email = current_user.email

        if old_email != email:
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email ID already taken! Try a different one')
                return redirect('edit_patient_profile')
            else:
                current_user.email = email

        number = request.POST.get('num')
        old_number = current_doctor.number

        if old_number != number:
            if number and Patients.objects.exclude(id=current_doctor.id).filter(number=number).exists():
                messages.error(request, 'Number already exists! Try a different one')
                return redirect('edit_patient_profile')
            else:
                current_doctor.number = number

        current_doctor.age = request.POST.get('age')
        remove_photo = request.POST.get('remove')

        if request.FILES.get('img'):
            current_doctor.image = request.FILES['img']

        if remove_photo == 'True':
            current_doctor.image = 'images/OtherUser.jpg'

        current_user.save()
        current_doctor.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('PatientHome')

    return redirect('edit_patient_profile')

@login_required
def reset_passwords(request):
    doct_id = request.user
    doctor = Doctors.objects.get(user_member = doct_id)
    PendingNotification = Notification.objects.filter(status = 'NEW',doctor = doctor)
    NotificationCount = PendingNotification.count()
    current = request.user.id
    usr = Doctors.objects.get(user_member=request.user)
    tcr = CustomUser.objects.get(id=current)
    current_teacher = request.user
    password = CustomUser.objects.get(username = current_teacher)
    return render(request, 'doctor/ResetPassword.html', {'password': password , 'tcr':tcr,'usr':usr, 'PendingNotification':PendingNotification, 'NotificationCount':NotificationCount})

@login_required
def reset_patients_passwords(request):

    current = request.user.id
    usr = Patients.objects.get(user_member=request.user)
    tcr = CustomUser.objects.get(id=current)
    current_teacher = request.user
    password = CustomUser.objects.get(username = current_teacher)
    return render(request, 'patient/ResetPassword.html', {'password': password , 'tcr':tcr,'usr':usr})

@login_required
def reset_password(request):
    if request.method == 'POST':
        current_password = request.POST['current']
        new_password = request.POST['passwd']
        confirm_password = request.POST['cpasswd']

        current_teacher = request.user
        user = CustomUser.objects.get(username=current_teacher)
        
        if not check_password(current_password, user.password):
            messages.error(request, 'Current password is incorrect!')
            return redirect('reset_passwords')

        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return redirect('reset_passwords')

        if not re.search(r'\d', new_password):
            messages.error(request, 'Password must contain at least one number!')
            return redirect('reset_passwords')

        if not re.search(r'[A-Z]', new_password):
            messages.error(request, 'Password must contain at least one capital letter!')
            return redirect('reset_passwords')

        if not re.search(r'[^\w\s]', new_password):
            messages.error(request, 'Password must contain at least one special character!')
            return redirect('reset_passwords')

        if new_password == confirm_password:
            user.password = make_password(new_password)
            user.save()
            messages.success(request, 'Password Changed Successfully!')
            return redirect('LoginPage')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('reset_passwords')
            
    return redirect('reset_passwords')

@login_required
def reset_password_patient(request):
    if request.method == 'POST':
        current_password = request.POST['current']
        new_password = request.POST['passwd']
        confirm_password = request.POST['cpasswd']

        current_teacher = request.user
        user = CustomUser.objects.get(username=current_teacher)
        
        if not check_password(current_password, user.password):
            messages.error(request, 'Current password is incorrect!')
            return redirect('reset_patients_passwords')

        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return redirect('reset_patients_passwords')

        if not re.search(r'\d', new_password):
            messages.error(request, 'Password must contain at least one number!')
            return redirect('reset_patients_passwords')

        if not re.search(r'[A-Z]', new_password):
            messages.error(request, 'Password must contain at least one capital letter!')
            return redirect('reset_patients_passwords')

        if not re.search(r'[^\w\s]', new_password):
            messages.error(request, 'Password must contain at least one special character!')
            return redirect('reset_patients_passwords')

        if new_password == confirm_password:
            user.password = make_password(new_password)
            user.save()
            messages.success(request, 'Password Changed Successfully!')
            return redirect('LoginPage')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('reset_patients_passwords')
            
    return redirect('reset_patients_passwords')

def AppoinmentDoctor(request):

    usr = Patients.objects.get(user_member=request.user)
    doct = Doctors.objects.all()
    return render(request, 'patient/AppoinmentDoctor.html', {'usr':usr, 'doct':doct})

def AppoinmentDoctorReport(request):

    if request.method == 'POST':
        usr = Patients.objects.get(user_member=request.user)
        user_id = request.POST.get('sel')
        pat_id = request.user.id

        pat = Patients.objects.get(user_member = pat_id)

        try:
            doct = Doctors.objects.get(id=user_id)
            appoinment = Appoinment.objects.filter(doctor=doct, patient=pat).order_by('-id')
        except Appoinment.DoesNotExist:
            appoinment = None 

        return render(request, 'patient/AppoinmentDoctorReport.html', {'appoinment':appoinment, 'doct':doct , 'usr':usr })
  
def DateAppoinment(request):

    usr = Patients.objects.get(user_member=request.user)
    return render(request, 'patient/DateAppoinment.html', {'usr':usr})

def DateAppoinmentReport(request):

    if request.method == 'POST':
        usr = Patients.objects.get(user_member=request.user)
        date = request.POST.get('date')
        pat_id = request.user.id

        pat = Patients.objects.get(user_member = pat_id)

        try:
            
            appoinment = Appoinment.objects.filter(date=date, patient=pat).order_by('-id')
        except Appoinment.DoesNotExist:
            appoinment = None 

        return render(request, 'patient/DateAppoinmentRecord.html', {'appoinment':appoinment, 'usr':usr })
  
def AddDoctorPage(request):

    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()
    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()
    departments = Departments.objects.all()

    return render(request, 'admin/AddDoctor.html',{'departments':departments, 'pending_users': pending_users, 'pending_count': pending_count, 'PendingBooking':PendingBooking, 'BookingCount':BookingCount })

def AddDoctor(request):

    if request.method == 'POST':
        firstname = request.POST.get('Fname')
        lastname = request.POST.get('Lname')
        usename = request.POST.get('Username')
        age = request.POST.get('Age')
        gender = request.POST.get('Gender')
        number = request.POST.get('Phone')
        email = request.POST.get('Email')
        image = request.FILES.get('Photo')
        cv = request.FILES.get('cv')
        type = '2'
        password = str(random.randint(100000,999999))
        sel = request.POST.get('department')
        department_name = Departments.objects.get(id=sel)
        if image == None:
                if gender == 'Male':
                    image = 'images/MaleUser.jpg'
                elif gender == 'Female':
                    image = 'images/FemaleUser.jpg'
                else:
                    image = 'images/OtherUser.jpg'
        if CustomUser.objects.filter(username=usename).exists(): 
            messages.error(request,'Username already exists, Try a new one')
            return redirect('AddDoctorPage')
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request,'Email already exists, Try a new one')
            return redirect('AddDoctorPage')
        
        elif Patients.objects.filter(number=number).exists():
            messages.error(request,'Phone Number already exists, Try a new one')
            return redirect('AddDoctorPage')

        else:
            user = CustomUser.objects.create_user(username=usename,password=password,email=email,first_name=firstname,last_name=lastname,user_type=type,is_active=True)
            user.save()
            pat = Doctors(user_department = department_name,age =age,gender = gender, number =number,cv=cv,image=image,user_member=user)
            pat.save()
            
            subject = 'Registration Approved as Doctor'
            message = f"Hello {usename},\n Your username is {usename} and your password is {password} \n Your Doctor ID is {user.id}"
            send_mail(subject,message ,settings.EMAIL_HOST_USER,{email})
           
            messages.success(request, 'Added Doctor Successfully')
            return redirect('AddDoctorPage')
    
    else:
        return redirect('AddDoctorPage')
    
def AddPatientPage(request):

    pending_users = CustomUser.objects.filter(is_active=False)
    pending_count = pending_users.count()

    PendingBooking = Appoinment.objects.filter(status = 'PENDING')
    BookingCount = PendingBooking.count()
    return render(request, 'admin/AddPatient.html',{'pending_users': pending_users, 'pending_count': pending_count, 'PendingBooking':PendingBooking, 'BookingCount':BookingCount })

def AddPatient(request):
    if request.method == 'POST':
        firstname = request.POST.get('Fname')
        lastname = request.POST.get('Lname')
        usename = request.POST.get('Username')
        age = request.POST.get('Age')
        gender = request.POST.get('Gender')
        number = request.POST.get('Phone')
        email = request.POST.get('Email')
        image = request.FILES.get('Photo')
        type = '3'
        password = str(random.randint(100000,999999))
        if image == None:
                if gender == 'Male':
                    image = 'images/MaleUser.jpg'
                elif gender == 'Female':
                    image = 'images/FemaleUser.jpg'
                else:
                    image = 'images/OtherUser.jpg'
        if CustomUser.objects.filter(username=usename).exists(): 
            messages.error(request,'Username already exists, Try a new one')
            return redirect('AddPatientPage')
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request,'Email already exists, Try a new one')
            return redirect('AddPatientPage')
        
        elif Patients.objects.filter(number=number).exists():
            messages.error(request,'Phone Number already exists, Try a new one')
            return redirect('AddPatientPage')

        else:
            user = CustomUser.objects.create_user(username=usename,password=password,email=email,first_name=firstname,last_name=lastname,user_type=type,is_active=True)
            user.save()
            pat = Patients(age =age,gender = gender, number =number,image=image,user_member=user)
            pat.save()
            
            subject = 'Registration Approved as Patient'
            message = f"Hello {usename},\n Your username is {usename} and your password is {password} \n Your Patient ID is {user.id}"
            send_mail(subject,message ,settings.EMAIL_HOST_USER,{email})
           
            messages.success(request, 'Added Patient Successfully')
            return redirect('AddPatientPage')
    
    else:
        return redirect('AddPatientPage')