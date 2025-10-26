from django.test import TestCase
from users.models import User
from accounts.models import Account
from loans.models import Loan

class AccountModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="john_doe",
            email="john@example.com",
            password="pass1234"
        )
        self.account = Account.objects.create(
            user=self.user,
            account_number="1234567890",
            balance=1000.0
        )

    def test_deposit_increases_balance(self):
        old_balance = self.account.balance
        deposit_amount = 500.0
        self.account.deposit(deposit_amount)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, old_balance + deposit_amount)

    def test_withdraw_decreases_balance(self):
        old_balance = self.account.balance
        withdraw_amount = 200.0
        self.account.withdraw(withdraw_amount)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, old_balance - withdraw_amount)

    def test_withdraw_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(5000.0)

    def test_transfer_between_accounts(self):
        receiver = User.objects.create_user(username="mary", email="mary@example.com", password="pass1234")
        receiver_account = Account.objects.create(user=receiver, account_number="0987654321", balance=500.0)
        self.account.transfer(receiver_account, 300.0)
        self.account.refresh_from_db()
        receiver_account.refresh_from_db()
        self.assertEqual(self.account.balance, 700.0)
        self.assertEqual(receiver_account.balance, 800.0)


class LoanModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="peter", email="peter@example.com", password="pass1234")
        self.account = Account.objects.create(user=self.user, account_number="111122223333", balance=1000.0)
        self.loan = Loan.objects.create(
            user=self.user,
            amount=500.0,
            interest_rate=10.0,
            duration_months=6,
            status="PENDING"
        )

    def test_approve_loan_changes_status(self):
        self.loan.approve()
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.status, "APPROVED")

    def test_loan_repayment_reduces_balance(self):
        self.loan.approve()
        self.loan.repay(100)
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.amount_due, 400.0)
