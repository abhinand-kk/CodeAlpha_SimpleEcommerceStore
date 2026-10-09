# CodeAlpha Simple E-commerce Store

A robust, internship-level Simple E-commerce Store built with Python and Django. This project fulfills the requirements of the CodeAlpha Full Stack Development internship, implementing product listings, shopping cart logic, real-time stock validation, secure session handling, and transactional checkouts. No third-party API or JavaScript frameworks were used – everything runs locally using Django 5.2.18 and SQLite.

## Application Features

- **Product Management:** Complete administrative panel for adding and modifying products and tracking stock.
- **Dynamic Storefront:** Clean and responsive storefront showing active electronics/apparel with a cart count badge.
- **Robust Session Cart:** Add/Remove/Update items securely leveraging server-calculated pricing from active database records.
- **Authentication System:** Secure registration and login functionalities leveraging Django's native auth.
- **Atomic Checkout Logic:** Process demonstrations orders seamlessly with `transaction.atomic()`, handling stock deductions and preserving cart if any failure occurs mid-transaction.
- **Order History:** Users can trace prior placed orders containing snapshots of names and historical prices, preserving consistency even if products are later retired or renamed.

## Development Setup

### 1. Prerequisites
- Python 3.12+ 

### 2. Environment Setup
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Dependencies
Install the pinned dependencies relying on the LTS Django 5.2.18:
```powershell
python -m pip install -r requirements.txt
```

### 4. Database Initialization
Run the initial database structural migrations:
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Seeding Sample Products
Avoid an empty storefront by quickly seeding 8 diverse products ranging from Electronics to Home Appliances:
```powershell
python manage.py seed_data
```

### 6. Create Superuser (Admin)
Create an admin account to manage products and observe placed orders backend manually:
```powershell
python manage.py createsuperuser
```

### 7. Run Server
Boot up the development environment, running on port 8000:
```powershell
python manage.py runserver
```

## Running Automated Tests
Run the comprehensive unittests confirming cart boundaries, concurrency simulation rollbacks, and unauthenticated protections:
```powershell
python manage.py test shop
```
All 5 comprehensive simulation tests are structured across edge cases successfully triggering OK statuses without exception.
