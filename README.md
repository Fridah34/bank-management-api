# bank-management-api
Backend Bank Management API built with Django &amp; Django REST Framework


## 🚀 Features

- 👤 **User Authentication (JWT)** – Secure login & registration using JSON Web Tokens.  
- 💰 **Account Management** – Create, view, and manage customer bank accounts.  
- 💳 **Transactions** – Deposit, withdraw, and transfer funds between accounts.  
- 🧾 **Transaction History** – Track and view all transactions per account.  
- 🔐 **Role-based Access Control** – Separate privileges for admin and normal users.  
- 🧠 **Custom User Model** – Extended from Django’s base user to include more fields.  
- 📊 **Scalable API Design** – Clean structure for future extensions.  

---

## 🧩 Tech Stack

- **Backend Framework:** Django 5 / Django REST Framework  
- **Authentication:** JWT (`djangorestframework-simplejwt`)  
- **Database:** SQLite (can switch to PostgreSQL or MySQL)  
- **Language:** Python 3.12  
- **Version Control:** Git + GitHub

## 🏗️ Project Structure
bank-management-api/
│
├── accounts/ # Account and transaction management
├── users/ # Custom user model and authentication
├── bank_management_api/ # Main project settings
├── db.sqlite3 # Database file
├── manage.py # Django management script
└── README.md # Project documentation

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

bash

git clone https://github.com/<Fridah34>/bank-management-api.git
cd bank-management-api

Create a virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows 
#OR
source venv/bin/activate  #On macOS/Linux


#Install dependencies
pip install -r requirements.txt

#Apply migrations
python manage.py makemigrations
python manage.py migrate

#create a superuser
python manage.py createsuperuser


Run the development server
python manage.py runserver


🔑 Authentication Endpoints (JWT)
Method	   Endpoint	             Description
POST	   /api/token/	         Obtain access and refresh tokens
POST	  /api/token/refresh/	   Refresh access token
POST	  /api/users/register/	   Register a new user
POST	  /api/users/login/	      Login and get JWT tokens


💵 Account & Transaction Endpoints
Method	    Endpoint	                    Description
GET	     /api/accounts/	                 List all accounts
POST	   /api/accounts/	                 Create new account
GET	     /api/accounts/<id>/             Retrieve account details
POST	  /api/transactions/deposit/	     Deposit money
POST	  /api/transactions/withdraw/	     Withdraw money
POST	  /api/transactions/transfer/	     Transfer funds between accounts

🧑‍💻 Developer Notes

Always run migrations after pulling new changes.

Make sure your virtual environment is activated before installing dependencies.

Use environment variables to store sensitive credentials.

You can switch from SQLite to PostgreSQL easily by updating DATABASES in settings.py.

🧾 License

This project is licensed under the MIT License.


