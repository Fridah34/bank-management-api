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

#### Authentication Endpoints 
POST /api/auth/register/
   Content-Type: application/json
    
    Body
    {
      "username": "customer1",
      "email": "customer1@example.com",
      "password": "Customer@123"
    }

    ✅ Response

    {
      "id": 1,
      "username": "customer1",
      "email": "customer1@example.com",
      "role": "CUSTOMER"
    }

    ### Register an Admin

## You can create an admin using the Django shell:

python manage.py createsuperuser


Then login using the token endpoint below.

### Login (Customer or Admin)
POST /api/auth/login  /
Content-Type: application/json

Request Body
{
  "username": "customer1",
  "password": "Customer@123"
}

Response
 {
  "refresh": "<refresh_token>",
  "access": "<access_token>"
 }


Use this access token for Authorization headers:

Authorization: Bearer <access_token>

### Account Endpoints
## Create an account(Admin only)
POST /api/accounts/
 
 Body
 {
  "User": 8,
  "account_number": "ACC-1001",
  "balance": "1000.00"
 }
## Get All Accounts (Admin Only)
 GET /api/accounts/
 Authorization: Bearer <admin_token>

 Response

  {
    "id": 1,
    "user": "customer1",
    "balance": "10000.00",
    "created_at": "2025-10-27T10:45:12Z"
  }


### Get My Account (Customer)
 GET /api/accounts/me/
 Authorization: Bearer <customer_token>

  Response
  {
    "id": 1,
    "user": "customer1",
    "balance": "10000.00"
  }

#### Loan Endpoints
  Apply for a Loan (Customer)
  POST /api/loans/
  Authorization: Bearer <customer_token>
  Content-Type: application/json


  Request Body

  {
  "amount": 5000,
  "interest_rate": 10,
  "duration_months": 12
  }


✅ Response

{
  "id": 1,
  "status": "PENDING",
  "amount": "5000.00",
  "interest_rate": "10.00",
  "duration_months": 12,
  "user": "customer1"
}

 ### View My Loans (Customer)
  GET /api/loans/
  Authorization: Bearer <customer_token>

  Response
  {
    "id": 1,
    "status": "PENDING",
    "amount": "5000.00",
    "interest_rate": "10.00",
    "duration_months": 12
  }


#### Approve Loan (Admin)
  PUT /api/loans/1/approve/
 Authorization: Bearer <admin_token>

  Response
  {
    "id": 1,
    "status": "APPROVED",
    "reviewed_by": "admin",
    "approved_at": "2025-10-28T20:00:00Z"
  }

### Reject Loan (Admin)
  PUT /api/loans/1/reject/
  Authorization: Bearer <admin_token>

   Response

  {
    "id": 1,
    "status": "REJECTED",
    "reviewed_by": "admin"
  }

###  Mark Loan as Repaid (Admin)
  PUT /api/loans/1/mark_repaid/
  Authorization: Bearer <admin_token>

    Response
  {
    "id": 1,
    "status": "REPAID",
    "user": "customer1"
  }

 ### Audit Log (Admin Only)
GET /api/auditlogs/
Authorization: Bearer <admin_token>


✅ Response

[
  {
    "id": 3,
    "user": "customer1",
    "action": "loan_approve",
    "description": "Loan #1 approved for user customer1",
    "timestamp": "2025-10-28T21:40:00Z"
  }
]

👑 Roles Summary
Role	Permissions
Admin	Approve/Reject loans, view all users/accounts, access audit logs
Customer	Register, login, apply for loans, view their own accounts/loans

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


