from django.contrib.auth import authenticate, login, get_user_model,logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
import random
from django.conf import settings
from .models import EmailOTP
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from product.models import Product
from orders.models import Order, OrderAddress



User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    user_obj = None

    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None


        if user_obj:
            if not user_obj.is_active:
                messages.error(request, "Your account is not verified. Please check your email for the verification .")
                return redirect('login')

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
            
        
          # আগে 'register' লেখা ছিল, সেটা ভুল ছিল

    return render(request, 'login.html')




def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')



    if request.method == 'POST':
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')


        # Step 1: Validate input

        if not firstname:
            messages.error(request, "First name is required.")
            return redirect('register')
        
        if not lastname:
            messages.error(request, "Last name is required.")
            return redirect('register')
        
        

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')
        
        
         

        # Extra fields
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        country = request.POST.get('country')
        mobile = request.POST.get('mobile')

        if not mobile:
            messages.error(request, "Number is required.")
            return redirect('register')
        
        if not address1:
            messages.error(request, "Address is required.")
            return redirect('register')
        
        if not city:
            messages.error(request, "City is required.")
            return redirect('register')
        
        if not postcode:
            messages.error(request, "Postcode is required.")
            return redirect('register')
        
        if not country:
            messages.error(request, "Country is required.")
            return redirect('register')
        
        if not password1:
            messages.error(request, "Password is required.")
            return redirect('register')
        
        if not password2:
            messages.error(request, "Confirm password is required.")
            return redirect('register')
        

        if not username:
            messages.error(request, "Username is required.")
            return redirect('register')
        
        if not email:
            messages.error(request, "Email is required.")
            return redirect('register')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')




        

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = firstname
        user.last_name = lastname
        user.is_active = False # ❌ ইউজার এক্টিভ না, OTP ভেরিফাই করার আগ পর্যন্ত

        # যদি Custom User Model ব্যবহার করো তবে নিচের লাইনগুলো কাজ করবে
        user.address_line_1 = address1
        user.address_line_2 = address2
        user.city = city
        user.postcode = postcode
        user.country = country
        user.mobile = mobile

        user.save()

        # Step 3: Generate OTP
        otp_code = str(random.randint(100000, 999999))
        EmailOTP.objects.create(user=user, otp=otp_code)


        # Step 4: Send OTP to email
        send_mail(
            subject='Your OTP Code',
            message=f'Hello {firstname},\n\nYour OTP is: {otp_code}\n\nThis will expire in 5 minutes.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        # Step 5: Save email in session for verify step
        request.session['pending_email'] = email
        messages.success(request, "OTP sent to your email. Please verify.")
        return redirect('verify')  # এখানে OTP verification page-এ পাঠিয়ে দিচ্ছি

    return render(request, 'register.html')



def verify_view(request):
    email = request.session.get('pending_email')
    if not email:
        return redirect('register')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        otp_record = EmailOTP.objects.filter(user__email=email).order_by('-created_at').first()


        if not otp_record:
            messages.error(request, "No OTP found. Please register again.")
            return redirect('register')

        if timezone.now() - otp_record.created_at > timezone.timedelta(minutes=5):
            otp_record.delete()
            messages.error(request, "OTP expired. Please register again.")
            return redirect('register')

        if otp_record.otp == otp_input:
            user = get_user_model().objects.get(email=email)
            user.is_active = True
            user.save()
            otp_record.delete()
            messages.success(request, "Your email is verified. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP.")
            return render(request, 'verify.html')

    return render(request, 'verify.html')




@login_required
def profile_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to view this page.")
        return redirect('login')
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')

    # অর্ডার সংখ্যা গোনা
    total_orders = orders.count()
    pending_orders = orders.filter(order_status='pending').count()
    delivered_orders = orders.filter(order_status='delivered').count()
    in_transit_orders = orders.filter(order_status='shipped').count() + orders.filter(order_status='processing').count()

    recent_orders = orders[:5]  # সর্বশেষ ৫টি অর্ডার দেখানো হবে

    context = {
        'user': user,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'in_transit_orders': in_transit_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard.html', context)






def logout_view(request):
    logout(request)  # ইউজার লগআউট করানো হলো
    messages.success(request, "Logged out successfully.")
    return redirect('login')



def my_orders_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to view this page.")
        return redirect('login')
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')

    # অর্ডার সংখ্যা গোনা
    total_orders = orders.count()
    pending_orders = orders.filter(order_status='pending').count()
    delivered_orders = orders.filter(order_status='delivered').count()
    in_transit_orders = orders.filter(order_status='shipped').count() + orders.filter(order_status='processing').count()

    recent_orders = orders[:5]  # সর্বশেষ ৫টি অর্ডার দেখানো হবে

    context = {
        'user': user,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'in_transit_orders': in_transit_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'my_orders.html', context)
    

def order_detail_view(request,):
    
        return redirect('login')


def order_success_view(request, order_id):
    if request.user.is_authenticated:
        order = Order.objects.get(id=order_id, user=request.user)
        return render(request, 'order_success.html', {'order': order})
    else:
        messages.error(request, "You need to be logged in to view this page.")
        return redirect('login')
    
def dashboard_view(request):
    if request.user.is_authenticated:
        user = request.user
        products = Product.objects.all()  # Assuming you want to show all products
        return render(request, 'dashboard.html', {'user': user, 'products': products})
    else:
        messages.error(request, "You need to be logged in to view this page.")
        return redirect('login')
    


def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, "Email is required.")
            return redirect('password_reset_request')

        try:
            user = User.objects.get(email=email)

            # Generate OTP
            otp_code = str(random.randint(100000, 999999))

            # Save OTP
            EmailOTP.objects.create(user=user, otp=otp_code)

            # Send OTP via email
            send_mail(
                subject='Your Password Reset OTP',
                message=f'Hello {user.first_name},\n\nYour password reset OTP is: {otp_code}\n\nThis will expire in 5 minutes.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            # Save email in session
            request.session['reset_email'] = email
            messages.success(request, "OTP sent to your email.")
            return redirect('password_reset_verify')

        except User.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect('password_reset_request')

    return render(request, 'password_reset_email.html')



def password_reset_verify(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, "Session expired. Try again.")
        return redirect('password_reset_request')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        otp_record = EmailOTP.objects.filter(user__email=email).order_by('-created_at').first()

        if not otp_record:
            messages.error(request, "No OTP found. Please request again.")
            return redirect('password_reset_request')

        if timezone.now() - otp_record.created_at > timezone.timedelta(minutes=5):
            otp_record.delete()
            messages.error(request, "OTP expired. Please request again.")
            return redirect('password_reset_request')

        if otp_record.otp == otp_input:
            otp_record.delete()  # Use-once policy
            messages.success(request, "OTP verified. You can now reset your password.")
            return redirect('password_reset_confirm')
        else:
            messages.error(request, "Invalid OTP.")
            return render(request, 'password_reset_verify.html')

    return render(request, 'password_reset_verify.html')



def password_reset_confirm(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, "Session expired. Try again.")
        return redirect('password_reset_request')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not password1 or not password2:
            messages.error(request, "Both fields are required.")
            return redirect('password_reset_confirm')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('password_reset_confirm')

        try:
            user = User.objects.get(email=email)
            user.set_password(password1)
            user.save()

            # Clear session
            del request.session['reset_email']
            messages.success(request, "Password reset successful. Please log in.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('password_reset_request')

    return render(request, 'password_reset_confirm.html')



def account_settings_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to view this page.")
        return redirect('login')
    
    user = request.user
    return render(request, 'account_settings.html', {'user': user})




@login_required
def update_profile_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in.")
        return redirect('login')
    
    user = request.user

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')

        # Extra fields
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        country = request.POST.get('country')
        mobile = request.POST.get('mobile')

        # Input Validation
        if not all([first_name, last_name, username, address1, city, postcode, country, mobile]):
            messages.error(request, "All fields except Address Line 2 are required.")
            return redirect('update_profile')

        if User.objects.exclude(pk=user.pk).filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('update_profile')

        # Update user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.address_line_1 = address1
        user.address_line_2 = address2
        user.city = city
        user.postcode = postcode
        user.country = country
        user.mobile = mobile
        user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('dashboard')

    return render(request, 'update_profile.html', {'user': user})



from django.contrib.auth import logout

def update_password_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to view this page.")
        return redirect('login')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # Validate input fields
        if not all([current_password, new_password1, new_password2]):
            messages.error(request, "All password fields are required.")
            return redirect('update_password')
        
        if new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
            return redirect('update_password')

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('update_password')

        # Update password and logout
        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, "Password updated successfully. Please log in again.")
        logout(request)
        return redirect('login')

    return render(request, 'update_password.html')



def update_address_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to view this page.")
        return redirect('login')
    
    user = request.user

    if request.method == 'POST':
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        country = request.POST.get('country')
        mobile = request.POST.get('mobile')

        # Validate input
        if not address1:
            messages.error(request, "Address is required.")
            return redirect('update_address')
        if not city:
            messages.error(request, "City is required.")
            return redirect('update_address')
        if not postcode:
            messages.error(request, "Postcode is required.")
            return redirect('update_address')
        if not country:
            messages.error(request, "Country is required.")
            return redirect('update_address')
        if not mobile:
            messages.error(request, "Mobile number is required.")
            return redirect('update_address')

        # Update user address
        user.address_line_1 = address1
        user.address_line_2 = address2
        user.city = city
        user.postcode = postcode
        user.country = country
        user.mobile = mobile
        user.save()
        messages.success(request, "Address updated successfully.")
        return redirect('account_settings')
    return render(request, 'update_address.html', {'user': user})



def track_order_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to view this page.")
        return redirect('login')

    if request.method == 'POST':
        order_number = request.POST.get('order_number')

        # Order খোঁজা হচ্ছে
        try:
            order = Order.objects.get(order_number=order_number, user=request.user)
            products = order.items.all()  # ধরলাম order এর সাথে related name 'items'
            context = {
                'order_number': order_number,
                'products': products,
            }
            return render(request, 'track_order.html', context)

        except Order.DoesNotExist:
            messages.error(request, 'Sorry! No order found with this number.')
            return redirect('track_order')

    return render(request, 'track_order.html')








    





