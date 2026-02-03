# 🏥 Blockchain-Based Medicine Authenticity System

## 📌 Project Overview

The **Blockchain-Based Medicine Authenticity System** is a web application built using **Django** and **Blockchain technology** to ensure the authenticity of medicines.
Manufacturers register medicine details on the blockchain, generating a **unique hash** and **QR code** for each medicine batch.
Consumers, pharmacists, and regulators can verify medicine authenticity by scanning the QR code and checking blockchain records.

This system helps prevent **counterfeit medicines**, ensures **data immutability**, and increases **trust in pharmaceutical supply chains**.

---

## 🎯 Objectives

* Prevent circulation of fake and duplicate medicines
* Ensure immutability of medicine records using blockchain
* Provide QR-based verification for easy authenticity checks
* Allow manufacturers to securely register medicine details

---

## 🚀 Features

* Manufacturer medicine registration
* Automatic blockchain hash generation
* Blockchain transaction storage
* Unique QR code generation per medicine batch
* Admin panel for managing medicines
* Secure and tamper-proof data storage

---

## 🛠️ Technologies Used

### Backend

* **Django** (Python Web Framework)

### Blockchain

* **Ethereum (Ganache – local blockchain)**
* **Web3.py**

### Other Libraries

* **Pillow** – image handling
* **qrcode** – QR code generation

### Database

* **SQLite** (default Django database)

---

## 📂 Project Structure

```
medicine_auth_system/
│
├── core/
│   ├── migrations/
│   ├── templates/
│   │   ├── home.html
│   │   └── add_medicine.html
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── medicine_auth/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
├── venv/
└── README.md
```

---

## ⚙️ Installation & Setup

### Step 1: Clone or Download Project

```bash
git clone <repository_url>
cd medicine_auth_system
```

---

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

---

### Step 3: Install Dependencies

```bash
pip install django pillow qrcode web3
```

---

### Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Step 5: Create Admin User

```bash
python manage.py createsuperuser
```

---

### Step 6: Run the Server

```bash
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000/
```

Admin Panel:

```
http://127.0.0.1:8000/admin/
```

---

## 🔗 Blockchain Setup (Ganache)

1. Install **Ganache**
2. Start a local blockchain on:

   ```
   http://127.0.0.1:7545
   ```
3. Copy an account **private key**
4. Add it in `views.py` for testing:

   ```python
   private_key = "YOUR_GANACHE_PRIVATE_KEY"
   ```

> ⚠️ **Note:** Never expose private keys in production.

---

## 🧾 How It Works

### Manufacturer Flow:

1. Manufacturer fills medicine details
2. System generates a **SHA-256 hash**
3. Hash is stored on blockchain
4. Blockchain transaction hash is saved
5. QR code is generated automatically

### Verification Flow:

1. User scans QR code
2. Blockchain transaction hash is retrieved
3. Data authenticity is verified from blockchain

---

## 🧠 Database Model

```python
class Medicine(models.Model):
    name = models.CharField(max_length=200)
    batch_no = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=200)
    manufacture_date = models.DateField()
    expiry_date = models.DateField()
    blockchain_hash = models.CharField(max_length=256)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
```

---

## 🔐 Security Benefits

* Blockchain ensures **immutability**
* QR codes prevent duplication
* Hashing guarantees uniqueness
* Admin-controlled manufacturer entry

---

## 📈 Future Enhancements

* Smart contracts for medicine registration
* Public verification portal
* Mobile app with QR scanner
* IPFS for decentralized storage
* Role-based access (Manufacturer / Distributor / Retailer)


