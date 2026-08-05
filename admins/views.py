from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.urls import reverse
from datetime import timedelta
import random
from pathlib import Path
from urllib.parse import urlencode

from users.models import CustomUser, generate_random_mobile
from .models import AdminOTP
from disaster_app.models import Dataset

# ================================
# ADMIN CREDENTIALS
# ================================
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin"

# ========

# ================================
# ADMIN LOGIN PAGE
# ================================
def admin_login_page(request):
    return render(request, 'adminLogin.html')

# ================================
# SEND OTP
# ================================
def send_otp(request):
    email = request.GET.get('email')
    try:
        validate_email(email)
    except ValidationError:
        return HttpResponse("invalid_email", status=400)
    if email != ADMIN_EMAIL:
        return HttpResponse("invalid_user", status=403)

    otp = str(random.randint(100000, 999999))
    AdminOTP.objects.filter(email=email).delete()
    AdminOTP.objects.create(email=email, otp=otp)

    send_mail(
        subject="Your Admin Login OTP",
        message=f"Your OTP for admin login is: {otp}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )
    print("Admin OTP:", otp)
    return HttpResponse("sent")

# ================================
# VERIFY OTP
# ================================
def verify_otp(request):
    email = request.GET.get('email')
    otp = request.GET.get('otp')
    expiry_time = timezone.now() - timedelta(minutes=5)

    valid = AdminOTP.objects.filter(email=email, otp=otp, created_at__gte=expiry_time).exists()
    if valid:
        AdminOTP.objects.filter(email=email).delete()
        request.session['otp_verified_admin'] = True
        return HttpResponse("verified")
    return HttpResponse("invalid")

# ================================
# ADMIN LOGIN
# ================================
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not request.session.get('otp_verified_admin'):
            return render(request, 'adminLogin.html', {"error": "OTP not verified"})

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            request.session.pop('otp_verified_admin', None)
            request.session['admin_logged'] = True
            return redirect('pending_users')

        return render(request, 'adminLogin.html', {"error": "Invalid Email or Password"})
    return render(request, 'adminLogin.html')

# ================================
# ADMIN DASHBOARD
# ================================
def admin_dashboard(request):

    total_users = CustomUser.objects.filter(is_superuser=False).count()
    pending_users = CustomUser.objects.filter(status="PENDING",is_superuser=False).count()
    accepted_users = CustomUser.objects.filter(status="APPROVED",is_superuser=False).count()

    context = {
        "total_users": total_users,
        "pending_users": pending_users,
        "accepted_users": accepted_users
    }

    return render(request, "adminDashboard.html", context)


# ================================
# USER LIST PAGES
# ================================
def pending_users(request):
    users = CustomUser.objects.filter(status='PENDING', is_superuser=False)
    for user in users:
        if not (user.mobile or "").strip():
            user.mobile = generate_random_mobile()
            user.save(update_fields=["mobile"])
    return render(request, 'pendingUsers.html', {
        'users': users,
        'success': request.GET.get('success'),
        'error': request.GET.get('error'),
    })

def accepted_users(request):
    users = CustomUser.objects.filter(status='APPROVED', is_superuser=False, is_staff=False)
    for user in users:
        if not (user.mobile or "").strip():
            user.mobile = generate_random_mobile()
            user.save(update_fields=["mobile"])
    return render(request, 'acceptedUsers.html', {
        'users': users,
        'success': request.GET.get('success'),
        'error': request.GET.get('error'),
    })

def rejected_users(request):
    users = CustomUser.objects.filter(status='DENIED', is_superuser=False)
    for user in users:
        if not (user.mobile or "").strip():
            user.mobile = generate_random_mobile()
            user.save(update_fields=["mobile"])
    return render(request, 'rejectedUsers.html', {
        'users': users,
        'success': request.GET.get('success'),
        'error': request.GET.get('error'),
    })

@require_POST
def accept_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.status = 'APPROVED'
    user.save()
    query = urlencode({'success': 'User accepted successfully.'})
    return redirect(f"{reverse('accepted_users')}?{query}")

@require_POST
def reject_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.status = 'DENIED'
    user.save()
    query = urlencode({'success': 'User rejected successfully.'})
    return redirect(f"{reverse('rejected_users')}?{query}")

# ================================
# OTHER ADMIN PAGES
# ================================
def all_users(request):
    users = CustomUser.objects.filter(is_superuser=False)
    for user in users:
        if not (user.mobile or "").strip():
            user.mobile = generate_random_mobile()
            user.save(update_fields=["mobile"])
    return render(request, 'allUsers.html', {'users': users})
def upload_dataset(request):
    if request.method == "POST":
        dataset_name = (request.POST.get('dataset_name') or '').strip()
        dataset_file = request.FILES.get('dataset_file')

        if not dataset_name:
            query = urlencode({'error': 'Dataset name is required.'})
            return redirect(f"{reverse('admin_upload_dataset')}?{query}")
        if not dataset_file:
            query = urlencode({'error': 'Dataset file is required.'})
            return redirect(f"{reverse('admin_upload_dataset')}?{query}")

        Dataset.objects.create(name=dataset_name, file=dataset_file)
        query = urlencode({'success': 'Dataset uploaded successfully.'})
        return redirect(f"{reverse('admin_upload_dataset')}?{query}")

    context = {
        'success': request.GET.get('success'),
        'error': request.GET.get('error'),
    }
    return render(request, 'uploadDataset.html', context)

def view_dataset(request):
    datasets = []
    for data in Dataset.objects.all().order_by('-uploaded_at'):
        file_name = Path(data.file.name).name
        datasets.append({
            'id': data.id,
            'dataset_name': data.name,
            'dataset_type': Path(file_name).suffix.replace('.', '').upper() or 'FILE',
            'source': 'Database Upload',
            'uploaded_on': data.uploaded_at,
            'file_name': file_name,
        })

    return render(request, 'viewDataset.html', {'datasets': datasets})


def admin_download_dataset(request):
    dataset_id = request.GET.get('id')
    if not dataset_id:
        return HttpResponse("Missing dataset id.", status=400)

    dataset = Dataset.objects.filter(id=dataset_id).first()
    if not dataset or not dataset.file:
        return HttpResponse("File not found.", status=404)

    file_path = Path(dataset.file.path)
    if not file_path.exists() or not file_path.is_file():
        return HttpResponse("File not found.", status=404)

    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_path.name)


def admin_preview_dataset(request):
    dataset_id = request.GET.get('id')
    if not dataset_id:
        return JsonResponse({'error': 'Missing dataset id.'}, status=400)

    dataset = Dataset.objects.filter(id=dataset_id).first()
    if not dataset or not dataset.file:
        return JsonResponse({'error': 'File not found.'}, status=404)

    file_path = Path(dataset.file.path)
    if not file_path.exists() or not file_path.is_file():
        return JsonResponse({'error': 'File not found.'}, status=404)

    try:
        if file_path.suffix.lower() == '.csv':
            try:
                df = pd.read_csv(file_path, encoding='utf-8', nrows=10)
            except Exception:
                df = pd.read_csv(file_path, encoding='latin1', nrows=10)

            return JsonResponse({
                'file_name': file_path.name,
                'columns': list(df.columns),
                'rows': df.fillna('').astype(str).values.tolist(),
            })

        return JsonResponse({'error': 'Preview is supported only for CSV files.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

import pandas as pd
import joblib
from django.shortcuts import render
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from disaster_app.nn_model import FeatureExtractor
import torch

def graph_analysis(request):
    from disaster_app.views import get_model_metrics

    rf_metrics = get_model_metrics('rf')
    lr_metrics = get_model_metrics('lr')
    svm_metrics = get_model_metrics('svm')
    knn_metrics = get_model_metrics('knn')
    proposed_metrics = get_model_metrics('neural_xgb')

    # ==========================================================
    # Send To Template
    # ==========================================================

    context = {
        "labels": ["Accuracy", "Precision", "Recall", "F1 Score"],
        "sgdcData": [rf_metrics['accuracy'], rf_metrics['precision'], rf_metrics['recall'], rf_metrics['f1']],
        "lgbData": [lr_metrics['accuracy'], lr_metrics['precision'], lr_metrics['recall'], lr_metrics['f1']],
        "svmData": [svm_metrics['accuracy'], svm_metrics['precision'], svm_metrics['recall'], svm_metrics['f1']],
        "knnData": [knn_metrics['accuracy'], knn_metrics['precision'], knn_metrics['recall'], knn_metrics['f1']],
        "proposedData": [proposed_metrics['accuracy'], proposed_metrics['precision'], proposed_metrics['recall'], proposed_metrics['f1']],
        "datasetName": "EM-DAT Disaster Dataset"
    }

    return render(request, 'graphAnalysis.html', context)



def admin_run_model(request):
    return render(request, 'admin_run_model.html')


def run_rf_model(request):
    return render(request,'run_rf_model.html')
def run_lr_model(request):
    return render(request,'run_lr_model.html')
def run_svm_model(request):
    return render(request,'run_svm_model.html')
def run_knn_model(request):
    return render(request,'run_knn_model.html')

# ================================
# LOGOUT
# ================================
def admin_logout(request):
    request.session.flush()
    return redirect('adminLogin')

# ================================
# CHECK ADMIN CREDENTIALS (AJAX)
# ================================
def check_admin_credentials(request):
    email = request.GET.get("email")
    password = request.GET.get("password")
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        return HttpResponse("valid")
    return HttpResponse("invalid")
