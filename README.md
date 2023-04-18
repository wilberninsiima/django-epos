
# Supermarket ePOS (Point of Sales System) - Django




## Technology Used

**Fontend:** HTML, CSS, JavaScript(jQuery), Boostrap, DataTables, HTMX

**Backend:** Django, Python, Ajax, MySQL


## Features

- Login Page with User authentication
- User Access control and Management
- Dashboard Page with statistics and graphs
- DataTables with print, copy, to CSV, and to PDF buttons
- Product Categories Management (CRUD)
- Point of Sale (POS)
- Search and add product to list
- Graphically (GUI) picking items from list
- Calculate automatically the subtotal, grand total, tax amount
- Update Item Quantity and Recalculate Total
- Sale validation paid amount and at least one product
- Sales Management
- List all Sales
- View Sale details
- Print Sales Receipt





## Installation

To install this project, first clone this repository to your local directory

```bash
  git clone https://github.com/wilberninsiima/django-epos.git
```
Go to the project directory
```bash
cd django-pos
```
Create a virtual environment :
PowerShell:

```bash
python -m venv venv
venv\Scripts\Activate.ps1
```
Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```


## Run the project locally
Go to the project directory: 
```bash
django_point_of_sale
```

Make database migrations:
```bash
python manage.py makemigrations and python manage.py migrate
```

Create superuser 
```bash
python manage.py createsuperuser
```

with the following data: username: admin, password: admin, email: admin@admin

Run the server: python manage.py runserver

Open a browser and go to: http://127.0.0.1:8000/
## Authors

- [@wilberninsiima](https://github.com/wilberninsiima)

