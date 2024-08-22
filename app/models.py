from .extentions import db
from pytz import timezone 
from datetime import datetime, timedelta

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String[50])
    email = db.Column(db.String[50], unique = True, nullable = False)
    contact = db.Column(db.String[10], unique = True, nullable = False)
    dob = db.Column(db.Date)
    blood_group = db.Column(db.Enum("O+","O-","A+","A-","B+","B-","AB+","AB-", name='blood_group_enum'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    role = db.Column(db.Enum("User","DonorManager","InventoryManager","BankManager","Hospital", name='role_enum'), nullable=False, default="User")
    refresh_token = db.Column(db.String(128))


class BloodDonation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    donated_on = db.Column(db.DateTime, default = datetime.now(timezone("Asia/Kolkata")))
    expiry = db.Column(db.DateTime, default = datetime.now(timezone("Asia/Kolkata"))+ timedelta(days=42))
    quantity = db.Column(db.Numeric, nullable = False)
    blood_group = db.Column(db.Enum("O+","O-","A+","A-","B+","B-","AB+","AB-", name='blood_group_enum'), nullable=False)
    donor = db.relationship('Donor', backref='donations')

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Numeric, nullable = False)
    blood_group = db.Column(db.Enum("O+","O-","A+","A-","B+","B-","AB+","AB-", name='blood_group_enum'), nullable=False)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_date = db.Column(db.DateTime, default = datetime.now(timezone("Asia/Kolkata")))
    quantity = db.Column(db.Numeric, nullable = False)
    blood_group = db.Column(db.Enum("O+","O-","A+","A-","B+","B-","AB+","AB-", name='blood_group_enum'), nullable=False)
    status = db.Column(db.Enum("Requested", "Processing", "Canclled", name = "status_enum"), default = 'Requested')
    fulfilled_qty = db.Column(db.Numeric, default = 0)