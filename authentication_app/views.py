from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import time
from django.urls import reverse
from django.utils.http import urlencode

from .models import Medicine, Manufacturer
from .forms import DrugForm
from .blockchain import register_drug, get_drug_from_blockchain


def home(request):
    return render(request, "home.html")


def manufacturer_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        gov_code = request.POST.get("gov_code")

        try:
            manufacturer = Manufacturer.objects.get(
                email=email,
                gov_code=gov_code,
                is_verified=True
            )

            if manufacturer.check_password(password):
                # Save login info AND allow one-time registration
                request.session["manufacturer_id"] = manufacturer.id
                request.session["can_register"] = True
                return redirect("add_medicine")
            else:
                error = "Incorrect password"

        except Manufacturer.DoesNotExist:
            error = "Invalid credentials or not verified"

        return render(request, "login.html", {"error": error})

    return render(request, "login.html")


def manufacturer_logout(request):
    request.session.flush()
    return redirect("manufacturer_login")


def add_medicine(request):
    manufacturer_id = request.session.get("manufacturer_id")
    can_register = request.session.get("can_register", False)

    # Protect the page: must be logged in AND have registration permission
    if not manufacturer_id or not can_register:
        request.session.flush()
        return redirect("manufacturer_login")

    manufacturer = get_object_or_404(Manufacturer, id=manufacturer_id)

    if request.method == "POST":
        form = DrugForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            batch = form.cleaned_data["batch"]
            expiry = form.cleaned_data["expiry"]

            # Solidity expects uint → convert date to timestamp
            expiry_timestamp = int(time.mktime(expiry.timetuple()))

            # Register on blockchain
            result = register_drug(
                name=name,
                batch=batch,
                manufacturer=manufacturer.name,
                expiry=expiry_timestamp
            )

            if not result or "tx_hash" not in result:
                return HttpResponse("❌ Blockchain transaction failed")

            # Ensure 0x prefix
            tx_hash = result["tx_hash"]
            if not tx_hash.startswith("0x"):
                tx_hash = "0x" + tx_hash

            # Save in database (QR code auto-generated in model)
            medicine = Medicine.objects.create(
                tx_hash=tx_hash,
                name=name,
                batch=batch,
                manufacturer=manufacturer,
                expiry=expiry
            )

            # Disable further registration until next login
            request.session["can_register"] = False

            return redirect("medicine_success", medicine_id=medicine.id)
    else:
        form = DrugForm()

    return render(request, "register.html", {"form": form})


def medicine_success(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)

    # Clear session completely so manufacturer must login again
    request.session.flush()

    return render(request, "medicine_added_successfully.html", {
        "medicine": medicine,
        "qr_url": medicine.qr_code.url if medicine.qr_code else None,
        "tx_hash": medicine.tx_hash
    })


def verify_medicine(request):
    if request.method == "POST":
        tx_hash = request.POST.get("tx_hash")
        if not tx_hash:
            return render(request, "verify.html", {"error": "Please enter a transaction hash."})

        # Redirect safely with GET parameter to avoid URL issues with 0x hashes
        base_url = reverse('verify_result')
        query_string = urlencode({'tx_hash': tx_hash})
        url = f"{base_url}?{query_string}"
        return redirect(url)

    return render(request, "verify.html")


def verify_result(request):
    tx_hash = request.GET.get("tx_hash")
    if not tx_hash:
        return render(request, "verify.html", {"error": "Transaction hash missing."})

    # Fetch from blockchain
    medicine_data = get_drug_from_blockchain(tx_hash)

    if medicine_data:
        # Include database details if available
        try:
            db_medicine = Medicine.objects.get(tx_hash=tx_hash)
            medicine_data.update({
                "batch": db_medicine.batch,
                "expiry": db_medicine.expiry,
                "tx_hash": db_medicine.tx_hash,
                "manufacturer": db_medicine.manufacturer.name,
                "name": db_medicine.name
            })
        except Medicine.DoesNotExist:
            medicine_data["tx_hash"] = medicine_data.get("tx_hash", None)
    else:
        medicine_data = None

    return render(request, "verify_result.html", {
        "medicine": medicine_data
    })
