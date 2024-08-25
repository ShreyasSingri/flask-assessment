from flask_restx import fields
from .extentions import api

signup_request_model = api.model("signupRequest",{
    "name":fields.String(required=True, description='Name of employee/Hospital'),
    "email" : fields.String(required=True, description='Email ID of user'),
    "password":fields.String(required=True, description='Password for future login'),
    "role":fields.String(required=True, description='Role of user: User, DonorManager, InventoryManager, BankManager, Hospital')
})

login_request_model = api.model("loginRequest",{
    "email" : fields.String(required=True, description='Email ID of user'),
    "password":fields.String(required=True, description='Password for login')
})

donor_request_model = api.model("donorRequest",{
    "name":fields.String(required=True, description='Name of Donor'),
    "email" : fields.String(required=True, description='Email ID of Donor'),
    "contact" : fields.String(required=True, description='Contact No of Donor'),
    "dob": fields.Date(required=True, description='Date of birth of Donor'),
    "blood_group":fields.String(required=True, description='Blood Group of Donor: O+, O-, A+, A-, B+, B-, AB+, AB-')
})

blood_donation_request_model = api.model("bloodRequest",{
    "email" : fields.String(description='Email ID of Donor'),
    "contact" : fields.String(description='Contact No of Donor'),
    "donor_id" : fields.Integer(description='Unique ID of Donor'),
    "quantity" : fields.Integer(required=True, description='Volume of blood donoted in ml'),
    "blood_group":fields.String(required=True, description='Blood Group of Donated blood: O+, O-, A+, A-, B+, B-, AB+, AB-')
})

blood_requirenment_request_model = api.model("bloodRequirenmentRequest",{
    "quantity" : fields.Integer(required=True, description='Volume of blood required in ml'),
    "blood_group":fields.String(required=True, description='Blood Group of Reciepent: O+, O-, A+, A-, B+, B-, AB+, AB-')
})

update_blood_requirenment_request_model = api.model("bloodRequirenmentRequest",{
    "id": fields.Integer(required=True, description='Unique ID of request'),
    "status":fields.String(description='Status of blood request'),
    "fulfilled_qty": fields.Integer(description='Volume of blood supplied in ml')
})

# Responce Models
donor_response_model = api.model("donorResponse",{
    "id": fields.Integer(required=True, description='Unique ID of Donor'),
    "name":fields.String(required=True, description='Name of Donor'),
    "email" : fields.String(required=True, description='Email ID of Donor'),
    "contact" : fields.String(required=True, description='Contact No of Donor'),
    "dob": fields.Date(required=True, description='Date of birth of Donor'),
    "blood_group":fields.String(required=True, description='Blood Group of Donor: O+, O-, A+, A-, B+, B-, AB+, AB-')
})

blood_donation_response_model = api.model("bloodResponse",{
    "id": fields.Integer(required=True, description='Unique ID of Donation'),
    "donor_id": fields.Integer(required=True, description='Unique ID of Donor'),
    "donated_on": fields.Date(required=True, description='Date and time when donation was made'),
    "expiry": fields.Date(required=True, description='Date and time of expiry of the collected blood'),
    "quantity" : fields.Integer(required=True, description='Volume of blood donoted in ml'),
    "blood_group":fields.String(required=True, description='Blood Group of Donor: O+, O-, A+, A-, B+, B-, AB+, AB-'),
    "status":fields.String(required=True, description='Status of blood request'),
    "donor":fields.Nested(donor_response_model, description='Donor information')
})

request_blood_response_model = api.model("bloodRequirenmentResponse",{
    "id": fields.Integer(required=True, description='Unique ID of Request'),
    "requested_by": fields.Integer(required=True, description='Unique ID of Hospital that requested'),
    "request_date": fields.Date(required=True, description='Date of request'),
    "quantity" : fields.Integer(required=True, description='Volume of blood requested in ml'),
    "blood_group":fields.String(required=True, description='Blood Group of Reciepent: O+, O-, A+, A-, B+, B-, AB+, AB-'),
    "status":fields.String(required=True, description='Status of blood request'),
    "fulfilled_qty": fields.Integer(required=True, description='Volume of blood supplied in ml')
})

inventory_response_model = api.model("inventoryResponse",{
    "id": fields.Integer(required=True, description='Unique ID of blood group'),
    "quantity" : fields.Integer(required=True, description='Volume of blood stored in ml'),
    "blood_group":fields.String(required=True, description='Blood Group of the stored bloo: O+, O-, A+, A-, B+, B-, AB+, AB-')
})