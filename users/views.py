import os
import random
import joblib
import numpy as np
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt

# Import models
from .models import UserOTP, generate_random_mobile

# Initialize User Model
User = get_user_model()

# -------------------------------------------------------------------------
# 1. STATIC PAGES
# -------------------------------------------------------------------------

def home_page(request):
    return render(request, 'index.html')

def about_page(request):
    return render(request, 'about.html')

def service_page(request):
    return render(request, 'service.html')

def causes_page(request):
    return render(request, 'causes.html')

def events_page(request):
    return render(request, 'events.html')

def contact_page(request):
    return render(request, 'contact.html')

def disaster_predict(request):
    return render(request, 'userPredict.html')



# -------------------------------------------------------------------------
# 2. USER AUTHENTICATION AJAX HELPERS
# -------------------------------------------------------------------------

@csrf_exempt
def check_user_credentials(request):
    """Used for real-time validation via AJAX"""
    email = request.GET.get("email")
    password = request.GET.get("password")
    user = authenticate(username=email, password=password)
    return HttpResponse("valid" if user else "invalid")

@csrf_exempt
def check_register_fields(request):
    """Checks if email is taken before form submission"""
    email = request.GET.get("email")
    name = request.GET.get("name")
    mobile = request.GET.get("mobile")
    password = request.GET.get("password")

    if not all([email, name, mobile, password]):
        return HttpResponse("empty")

    if User.objects.filter(username=email).exists():
        return HttpResponse("exists")

    return HttpResponse("ok")


# -------------------------------------------------------------------------
# 3. OTP SYSTEM (SEND & VERIFY)
# -------------------------------------------------------------------------

def user_send_otp(request):
    try:
        email = request.GET.get("email")
        if not email:
            return HttpResponse("failed")

        otp = str(random.randint(100000, 999999))

        # Clear old OTPs and save new one
        UserOTP.objects.filter(email=email).delete()
        UserOTP.objects.create(email=email, otp=otp)
        
        print(f'OTP generated for {email}: {otp}') # For local debugging

        send_mail(
            "Your OTP Verification",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return HttpResponse("sent")

    except Exception as e:
        print("OTP SEND ERROR:", e)
        return HttpResponse("email_error")

def user_verify_otp(request):
    email = request.GET.get("email")
    otp = request.GET.get("otp")

    if UserOTP.objects.filter(email=email, otp=otp).exists():
        UserOTP.objects.filter(email=email).delete()
        return HttpResponse("verified")

    return HttpResponse("invalid")


# -------------------------------------------------------------------------
# 4. REGISTRATION & LOGIN LOGIC
# -------------------------------------------------------------------------

def user_login_page(request):
    return render(request, 'userLogin.html')

def user_register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = (request.POST.get('mobile') or '').strip()
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            return render(request, "userLogin.html", {"error": "User already exists"})

        # Custom status field must exist in your Custom User Model
        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
            mobile=mobile if mobile else generate_random_mobile(),
            status="PENDING" 
        )
        return render(request, "userLogin.html", {"success": "Registration successful. Wait for admin approval."})
    return redirect('user_login_page')

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)

        if user:
            # Check custom approval status
            if user.status == "APPROVED":
                login(request, user)
                return redirect('/user-dashboard/')
            elif user.status == "PENDING":
                return render(request, "userLogin.html", {"error": "Your account is pending admin approval"})
            else:
                return render(request, "userLogin.html", {"error": "Your account has been denied by admin"})

        return render(request, "userLogin.html", {"error": "Invalid Login Credentials"})
    return render(request, "userLogin.html")

def user_dashboard(request):
    return render(request, 'user-dashboard.html')

@login_required(login_url='userLogin')
def user_profile(request):
    if request.method == "POST":
        user = request.user
        name = (request.POST.get("name") or "").strip()
        mobile = (request.POST.get("mobile") or "").strip()
        new_password = (request.POST.get("password") or "").strip()

        if not name:
            return render(request, 'userProfile.html', {"error": "Name is required."})

        user.first_name = name
        user.mobile = mobile if mobile else generate_random_mobile()

        if new_password:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
        else:
            user.save(update_fields=["first_name", "mobile"])

        return render(request, 'userProfile.html', {"success": "Profile updated successfully."})

    return render(request, 'userProfile.html')

def user_logout(request):
    logout(request)
    return redirect('/')


# -------------------------------------------------------------------------
# 5. MACHINE LEARNING PREDICTION
# -------------------------------------------------------------------------

def predict_result(request):
    if request.method == "POST":
        try:
            import torch
            import torch.nn as nn
            import joblib
            import numpy as np
            from django.shortcuts import render, redirect
            from django.conf import settings
            import os

            BASE_DIR = settings.BASE_DIR

            # -----------------------------
            # Load Models
            # -----------------------------
            xgb = joblib.load(os.path.join(BASE_DIR, "ml_models1/xgb_model.pkl"))
            scaler = joblib.load(os.path.join(BASE_DIR, "ml_models1/scaler.pkl"))
            country_encoder = joblib.load(os.path.join(BASE_DIR, "ml_models1/country_encoder.pkl"))
            iso_encoder = joblib.load(os.path.join(BASE_DIR, "ml_models1/iso_encoder.pkl"))
            disaster_subtype_encoder = joblib.load(os.path.join(BASE_DIR, "ml_models1/disaster subtype_encoder.pkl"))
            target_encoder = joblib.load(os.path.join(BASE_DIR, "ml_models1/target_encoder.pkl"))

            # -----------------------------
            # Rebuild FeatureNet
            # -----------------------------
            class FeatureNet(nn.Module):
                def __init__(self, input_dim, num_classes):
                    super().__init__()
                    self.fc1 = nn.Linear(input_dim, 64)
                    self.fc2 = nn.Linear(64, 32)
                    self.classifier = nn.Linear(32, num_classes)

                def forward(self, x):
                    x = torch.relu(self.fc1(x))
                    x = torch.relu(self.fc2(x))
                    return x

            input_dim = scaler.n_features_in_
            nn_model = FeatureNet(input_dim, num_classes=len(target_encoder.classes_))
            feature_path = os.path.join(BASE_DIR, "ml_models1/feature_nn.pt")
            try:
                state_dict = torch.load(feature_path, map_location=torch.device("cpu"), weights_only=True)
            except TypeError:
                state_dict = torch.load(feature_path, map_location=torch.device("cpu"))
            nn_model.load_state_dict(state_dict)
            nn_model.eval()

            # -----------------------------
            # Collect Inputs from Form
            # -----------------------------
            country = request.POST["country"].strip()
            iso = request.POST["iso"].strip()
            disaster_subtype = request.POST.get("disaster_subtype", "").strip()

            def safe_transform(encoder, values):
                classes_set = set(encoder.classes_)
                safe_values = [v if v in classes_set else encoder.classes_[0] for v in values]
                return encoder.transform(safe_values)

            country_enc = safe_transform(country_encoder, [country])[0]
            iso_enc = safe_transform(iso_encoder, [iso])[0]
            disaster_subtype_enc = safe_transform(disaster_subtype_encoder, [disaster_subtype])[0]

            input_data = [
                int(request.POST["total_deaths"]),
                int(request.POST["injured"]),
                int(request.POST["total_affected"]),
                float(request.POST["total_damage"]),
                float(request.POST["cpi"]),
                float(request.POST["magnitude"]),
                float(request.POST["latitude"]),
                float(request.POST["longitude"]),
                int(request.POST["start_year"]),
                int(request.POST["end_year"]),
                int(request.POST["start_month"]),
                int(request.POST["end_month"]),
                country_enc,
                iso_enc,
                disaster_subtype_enc
            ]

            # -----------------------------
            # Scale → NN → XGB
            # -----------------------------
            X = np.array(input_data).reshape(1, -1)
            X_scaled = scaler.transform(X)

            with torch.no_grad():
                nn_features = nn_model(torch.tensor(X_scaled, dtype=torch.float32)).numpy()

            prediction_encoded = xgb.predict(nn_features)
            prediction = target_encoder.inverse_transform(prediction_encoded)[0]

            return render(request, "predictionResult.html", {
                "prediction": prediction,
                "input_data": request.POST
            })

        except Exception as e:
            print("PREDICTION ERROR:", e)
            return render(request, "predictionResult.html", {"error": str(e)})

    return redirect("/user_disaster_predict/")
