from flask_restx import Resource, Namespace, marshal
from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from .extentions import db,bcrypt
from .params import (
    signup_request_model,
    login_request_model,
    donor_request_model,
    donor_response_model,
    blood_donation_request_model,
    blood_donation_response_model,
    blood_requirenment_request_model,
    request_blood_response_model,
    update_blood_requirenment_request_model,
    inventory_response_model
    )
from .models import Donor, User, BloodDonation, Inventory, Request, TokenBlocklist
from pytz import timezone 
from datetime import datetime

userNs = Namespace("user")
bankNs = Namespace("bank")

def register_routes(api):
    api.add_namespace(userNs)
    api.add_namespace(bankNs)

def is_authorised(roles):
    identity = get_jwt_identity()
    return identity and identity['role'] in roles

def supplyBlood(qty, blood):
    bloods = BloodDonation.query.filter(BloodDonation.blood_group == blood, BloodDonation.status == "Stored").all()
    q = 0
    ids = []
    for i in bloods:
        i.status="Supplied"
        q = q+i.quantity
        ids.append(i.id)
        if qty <= q:
            break
    db.session.commit()
    inven = Inventory.query.filter_by(blood_group=blood).first()
    inven.quantity = inven.quantity-q
    db.session.commit()
    return ids,q

@userNs.route("/signup")
class Signup(Resource):
    # Specify the type of request data that is expected
    @userNs.expect(signup_request_model, validate=True)
    @userNs.doc(description='Register a new user User, DonorManager, InventoryManager, BankManager, Hospital')
    def post(self):
        data = request.get_json()
        hashedPassword = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
        user = User.query.filter_by(email=data.get('email'))
        if user is not None:
            return {'message': 'User already registered'}, 400
        try:
            newUser = User(name=data.get('name'),email=data.get('email'),password=hashedPassword,role=data.get('role'))
            db.session.add(newUser)
            db.session.commit()
        except:
            return {'message':'Error while signing up. Please check the data and try again'}, 401
        return {'message': 'User registered successfully'}, 201

@userNs.route("/login")
class Login(Resource):
    @userNs.expect(login_request_model, validate=True)
    @userNs.doc(description='Login for authorizition.')
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(data.get('email')).first()
        if user and bcrypt.check_password_hash(user.password, data.get('password')):
            access_token = create_access_token(identity={'id':user.id, 'role':user.role})
            refresh_token = create_refresh_token(identity={'id':user.id, 'role':user.role})
            return {'message': "Login successful!", 'access_token':access_token, 'refresh_token':refresh_token}, 201
        return {'message': 'Invalid email ID or password'}, 400

@userNs.route("/refresh")
class Refresh(Resource):
    @jwt_required(refresh=True)
    @userNs.doc(description='Generate new access_token for authorizition of all employees and hospitals. (Provide refresh token as Bearer token)')
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token)

@userNs.route("/logout")
class Logout(Resource):
    @jwt_required(verify_type=False)
    @userNs.doc(description='Logout and clear the access_token usablity')
    def post(self):
        jwt = get_jwt()
        jti = jwt['jti']
        token = TokenBlocklist(jti=jti)
        db.session.add(token)
        db.session.commit()
        return {'message': 'Logged out successfully'}, 200

@bankNs.route("/addDonor")
class AddDonor(Resource):
    @jwt_required()
    @userNs.expect(donor_request_model, validate=True)
    @userNs.doc(description='Add new donor')
    # Specify the pre porcessing of the data into a list that will be of the format of response model
    @userNs.marshal_with(donor_response_model)
    def post(self):
        if not is_authorised(["User","DonorManager","BankManager"]):
            return {'message': 'Unauthorised Request'}, 403
        data = request.get_json()
        donor = Donor.query.filter_by(email=data.get('email'))
        if donor is not None:
            return {'message': 'Donor already registered'}, 400
        try:
            newDonor = Donor(name=data.get('name'),email=data.get('email'), contact = data.get('contact'), dob = data.get('dob'),blood_group = data.get('blood_group'))
            db.session.add(newDonor)
            db.session.commit()
        except:
            return {'message':'Error while adding donor. Please check the data and try again'}, 401
        return newDonor, 200

@bankNs.route("/addblood")
class AddBlood(Resource):
    @jwt_required()
    @userNs.expect(blood_donation_request_model, validate=True)
    @userNs.doc(description='Add blood donation and update inventory. (email and contact number of donor OR Donor ID required to add blood donation)')
    @userNs.marshal_with(blood_donation_response_model)
    def post(self):
        if not is_authorised(["User","DonorManager","InventoryManager","BankManager"]):
            return {'message': 'Unauthorised Request'}, 403
        data = request.get_json()
        donorId = data.get('donor_id')
        if donorId is None:
            donor = Donor.query.filter_by(email = data.get('email'), contact = data.get('contact')).first()
            if donor is None:
                return {'message':'Invalid email ID or contact'}, 400
            donorId=donor.id
        try:
            bloodDonation = BloodDonation(donor_id = donorId, quantity=data.get('quantity'), blood_group = data.get('blood_group'))
            db.session.add(bloodDonation)
            inventory = Inventory.query.filter_by(blood_group = data.get('blood_group')).first()
            if inventory is None:
                inventory = Inventory(quantity=data.get('quantity'), blood_group = data.get('blood_group'))
                db.session.add(inventory)
            else:
                inventory.quantity = inventory.quantity+data.get('quantity')
            db.session.commit()
        except:
            return {'message':'Error while adding blood donation. Please check the data and try again'}, 401
        return bloodDonation, 200

@bankNs.route("/requestblood")
class RequestBlood(Resource):
    @jwt_required()
    @userNs.expect(blood_requirenment_request_model, validate=True)
    @userNs.doc(description='Hospitals to raise a blood requirenment request.')
    @userNs.marshal_with(request_blood_response_model)
    def post(self):
        if not is_authorised(["Hospital"]):
            return {'message': 'Unauthorised Request'}, 403
        identity = get_jwt_identity()
        data = request.get_json()
        try:
            newRequest = Request(requested_by = identity['id'],quantity=data.get('quantity'),blood_group = data.get('blood_group'))
            db.session.add(newRequest)
            db.session.commit()
        except:
            return {'message':'Error while adding Blood Request. Please check the data and try again'}, 401
        return newRequest, 201

@bankNs.route("/updatebloodreq")
class UpdateRequest(Resource):
    @jwt_required()
    @userNs.expect(update_blood_requirenment_request_model, validate=True)
    @userNs.doc(description='Update existing blood request')
    @userNs.marshal_with(request_blood_response_model)
    def post(self):
        identity = get_jwt_identity()
        data = request.get_json()
        if identity['role']=='Hospital' and data['status'] != "Cancelled":
            return {'message': 'Not Authorised to perform any action other than cancel request'}, 400
        req = Request.query.filter_by(id=data.get('id')).first()
        if req is None:
            return {'message': 'Invalid Request ID'}, 400
        if data.get('status'):
            req.status=data.get('status')
        if data.get('fulfilled_qty'):
            if req.fulfilled_qty > data.get('fulfilled_qty'):
                return {'message': 'New fulfilled quantity is less then already fulfilled quantity. please try again'}, 400
            blood, qty = supplyBlood((req.fulfilled_qty - data.get('fulfilled_qty')),req['blood_group'])
            req.fulfilled_qty = req.fulfilled_qty+qty
            if not blood:
                return  {'message': 'Insuffecient Inventory'}, 400
        db.session.commit()
        return {"message": "Blood request fulfilled", "request": marshal(req, request_blood_response_model), "blood_packet_IDs":blood}, 200

@bankNs.route("/completebloodreq/<int:id>")
class CompleteRequest(Resource):
    @jwt_required()
    @userNs.doc(description="Complete hospital's blood request")
    @userNs.marshal_with(request_blood_response_model)
    def post(self, id):
        if not is_authorised(["User","InventoryManager","BankManager"]):
            return {'message': 'Unauthorised Request'}, 403
        req = Request.query.get(id)
        blood, qty =  supplyBlood((req.fulfilled_qty - req.quantity),req['blood_group'])
        if not blood:
            return  {'message': 'Insuffecient Inventory'}, 400
        req.fulfilled_qty = req.fulfilled_qty + qty
        req.status= "Completed"
        db.session.commit()
        return {"message": "Blood request fulfilled", "request": marshal(req, request_blood_response_model), "blood_packet_IDs":blood}, 200

@bankNs.route("/inventorystatus")
class InventoryStatus(Resource):
    @userNs.doc(description='Provide details of Inventory stored in blood bank')
    @userNs.marshal_list_with(inventory_response_model)
    def get(self):
        return Inventory.query.all(), 201

@bankNs.route("/deleteblood/<int:id>")
class DeleteBloodDonation(Resource):
    @jwt_required()
    @userNs.doc(description='Delete inacurate Blood Donation')
    def delete(self, id):
        if not is_authorised(["DonorManager","InventoryManager","BankManager"]):
            return {'message': 'Unauthorised Request'}, 403
        blood = BloodDonation.query.get(id)
        db.session.delete(blood)
        db.session.commit()
        return {'message': 'Blood donation deleted successfully'}, 200

@bankNs.route("/deletedonaor/<int:id>")
class DeleteDonor(Resource):
    @jwt_required()
    @userNs.doc(description='Delete inacurate blood donor information')
    def delete(self, id):
        if not is_authorised(["DonorManager","InventoryManager","BankManager"]):
            return {'message': 'Unauthorised Request'}, 403
        donor = Donor.query.get(id)
        db.session.delete(donor)
        db.session.commit()
        return {'message': 'Donor deleted successfully'}, 200

@bankNs.route("/updateexpired")
class ExpiredBlood(Resource):
    @jwt_required()
    @userNs.doc(description='Check for expired blood and update the database accordingly')
    @userNs.marshal_list_with(blood_donation_response_model)
    def get(self):
        if not is_authorised(["User","InventoryManager","BankManager"]):
            return {'message': 'Unauthorised Request'}, 403
        expired = BloodDonation.query.filter(BloodDonation.expiry <datetime.now(timezone("Asia/Kolkata")), BloodDonation.status == "Stored").all()
        if not expired:
            return {'message': 'No expired blood to discard'}, 200
        qty = {}
        for i in expired:
            i.status="Expired"
            qty[i.blood_group] = (qty.get('blood_group') or 0)+i.quantity
        db.session.commit()
        inven = Inventory.query.all()
        for i in inven:
            i.quantity = i.quantity - qty.get(i.blood_group)
        db.session.commit()
        return expired, 201

@bankNs.route("/openrequests")
class OpenRequests(Resource):
    @jwt_required()
    @userNs.doc(description='Get the list of blood requests that needs to be processed')
    @userNs.marshal_list_with(request_blood_response_model)
    def post(self):
        if not is_authorised(["User","InventoryManager","BankManager","Hospital"]):
            return {'message': 'Unauthorised Request'}, 403
        identity = get_jwt_identity()
        res = None
        if identity.role=='Hospital':
            res = Request.query.filter_by(requested_by=identity.id, status="Requested").all()
        res = Request.query.filter_by(status="Requested").all()
        return res, 200
