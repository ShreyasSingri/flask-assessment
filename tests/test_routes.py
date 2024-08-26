import json
from app.models import BloodDonation, Inventory
from pytz import timezone 
from datetime import datetime, timedelta

access_token = ''

def test_signup(test_client,init_database):
    data = {'name':'test_user','email':'test@xyz.com','password':'test_pwd','role':'BankManager'}
    response = test_client.post('/user/signup',headers={"Content-Type": "application/json"}, data=json.dumps(data))
    assert response.status_code == 201
    response1 = test_client.post('/user/signup',headers={"Content-Type": "application/json"}, data=json.dumps(data))
    assert response1.status_code == 400

def test_login(test_client,init_database):
    data = {'email':'test@xyz.com','password':'test_pwd'}
    response = test_client.post('/user/login',headers={"Content-Type": "application/json"}, data=json.dumps(data))
    assert response.status_code == 201
    res = json.loads(response.data.decode('utf8'))
    global access_token 
    access_token = 'Bearer ' + res['access_token']
    data['email']='wrongEmail'
    response1 = test_client.post('/user/login',headers={"Content-Type": "application/json"}, data=json.dumps(data))
    assert response1.status_code == 400

def test_addDonor(test_client,init_database):
    data = {'name':'donor1','email':'donor@gmail.com', 'contact':'123756', 'age':20,'blood_group':'O+'}
    response = test_client.post('/bank/addDonor',headers={"Content-Type": "application/json",'Authorization':access_token}, data=json.dumps(data))
    assert response.status_code == 200
    response = test_client.post('/bank/addDonor',headers={"Content-Type": "application/json",'Authorization':access_token}, data=json.dumps(data))
    assert response.status_code == 400
    response1 = test_client.post('/addDonor/addDonor',headers={"Content-Type": "application/json",'Authorization':access_token}, data=json.dumps(data))
    assert response1.status_code == 404

def test_addBlood(test_client,init_database):
    data = {'email':'donor@gmail.com', 'contact':'123756', 'quantity':100,'blood_group':'O+'}
    response = test_client.post('/bank/addBlood',headers={"Content-Type": "application/json",'Authorization':access_token}, data=json.dumps(data))
    assert response.status_code == 200
    data = {'donor_id':1, 'quantity':100,'blood_group':'O+'}
    response = test_client.post('/bank/addBlood',headers={"Content-Type": "application/json",'Authorization':access_token}, data=json.dumps(data))
    assert response.status_code == 200


def test_inventory(test_client,init_database):
    response = test_client.get('/bank/inventoryStatus',headers={"Content-Type": "application/json",'Authorization':access_token})
    assert response.status_code == 201

def test_hospital(test_client,init_database):
    data = {'name':'test_hospital','email':'test_hospital@xyz.com','password':'test_1_pwd','role':'Hospital'}
    response = test_client.post('/user/signup',headers={"Content-Type": "application/json"}, data=json.dumps(data))
    assert response.status_code == 201
    data = {'email':'test_hospital@xyz.com','password':'test_1_pwd'}
    response = test_client.post('/user/login',headers={"Content-Type": "application/json"}, data=json.dumps(data))
    assert response.status_code == 201
    res = json.loads(response.data.decode('utf8'))
    hospital_access = 'Bearer ' + res['access_token']
    hospital_refresh = 'Bearer ' + res['refresh_token']
    data = {'quantity':500,'blood_group':'O+'}
    response = test_client.post('/bank/requestBlood',headers={"Content-Type": "application/json",'Authorization':hospital_access}, data=json.dumps(data))
    assert response.status_code == 201
    response = test_client.get('/bank/openRequests',headers={"Content-Type": "application/json",'Authorization':hospital_access})
    assert response.status_code == 200
    data = {"id": 1,"status":"Cancelled"}
    response = test_client.post('/bank/updateBloodReq',headers={"Content-Type": "application/json",'Authorization':hospital_access}, data=json.dumps(data))
    assert response.status_code == 200
    data = {'quantity':200,'blood_group':'O+'}
    response = test_client.post('/bank/requestBlood',headers={"Content-Type": "application/json",'Authorization':hospital_access}, data=json.dumps(data))
    assert response.status_code == 201
    data = {"id": 2,"fulfilled_qty":100}
    response = test_client.post('/bank/updateBloodReq',headers={"Content-Type": "application/json",'Authorization':access_token}, data=json.dumps(data))
    assert response.status_code == 200
    response = test_client.get('/bank/openRequests',headers={"Content-Type": "application/json",'Authorization':access_token})
    assert response.status_code == 200
    response = test_client.get('/bank/completeBloodReq/2',headers={"Content-Type": "application/json",'Authorization':access_token})
    assert response.status_code == 200
    response = test_client.get('/user/refresh',headers={"Content-Type": "application/json",'Authorization':hospital_refresh})
    assert response.status_code == 200
    res = json.loads(response.data.decode('utf8'))
    hospital_access = 'Bearer ' + res['access_token']
    response = test_client.get('/user/logout',headers={"Content-Type": "application/json",'Authorization':hospital_access})
    assert response.status_code == 200

def test_expired(test_client,init_database):
    response = test_client.get('/bank/updateExpired',headers={"Content-Type": "application/json",'Authorization':access_token})
    assert response.status_code == 200
    bd = BloodDonation(donor_id = 1, quantity=200, blood_group = 'O+',donated_on = datetime.now(timezone("Asia/Kolkata"))- timedelta(days=43),expiry = datetime.now(timezone("Asia/Kolkata"))- timedelta(days=1))
    init_database.session.add(bd)
    inven = Inventory.query.filter_by(blood_group='O+').first()
    inven.quantity = inven.quantity+200
    init_database.session.commit()
    response = test_client.get('/bank/updateExpired',headers={"Content-Type": "application/json",'Authorization':access_token})
    assert response.status_code == 201

def test_delete(test_client,init_database):
    response = test_client.delete('/bank/deleteBlood/1',headers={"Content-Type": "application/json",'Authorization':access_token})
    assert response.status_code == 200
    data = {'name':'donor2','email':'donor2@gmail.com', 'contact':'123326', 'age':20,'blood_group':'AB+'}
    response = test_client.post('/bank/addDonor',headers={"Content-Type": "application/json",'Authorization':access_token}, data=json.dumps(data))
    assert response.status_code == 200
    response = test_client.delete('/bank/deleteDonaor/2',headers={"Content-Type": "application/json",'Authorization':access_token})
    assert response.status_code == 200

def test_unauthorised(test_client,init_database):
    data = {'email':'test_hospital@xyz.com','password':'test_1_pwd'}
    response = test_client.post('/user/login',headers={"Content-Type": "application/json"}, data=json.dumps(data))
    assert response.status_code == 201
    res = json.loads(response.data.decode('utf8'))
    hospital_access = 'Bearer ' + res['access_token']
    data = {'name':'donor1','email':'donor@gmail.com', 'contact':'123756', 'age':20,'blood_group':'O+'}
    response = test_client.post('/bank/addDonor',headers={"Content-Type": "application/json",'Authorization':hospital_access}, data=json.dumps(data))
    assert response.status_code == 403
    data = {'email':'donor@gmail.com', 'contact':'123756', 'quantity':100,'blood_group':'O+'}
    response = test_client.post('/bank/addBlood',headers={"Content-Type": "application/json",'Authorization':hospital_access}, data=json.dumps(data))
    assert response.status_code == 403
    data = {'quantity':500,'blood_group':'O+'}
    response = test_client.post('/bank/requestBlood',headers={"Content-Type": "application/json",'Authorization':access_token}, data=json.dumps(data))
    assert response.status_code == 403
    data = {"id": 2,"status":"Completed"}
    response = test_client.post('/bank/updateBloodReq',headers={"Content-Type": "application/json",'Authorization':hospital_access}, data=json.dumps(data))
    assert response.status_code == 400
    response = test_client.delete('/bank/deleteBlood/1',headers={"Content-Type": "application/json",'Authorization':hospital_access})
    assert response.status_code == 403
    response = test_client.delete('/bank/deleteDonaor/2',headers={"Content-Type": "application/json",'Authorization':hospital_access})
    assert response.status_code == 403
    response = test_client.get('/bank/updateExpired',headers={"Content-Type": "application/json",'Authorization':hospital_access})
    assert response.status_code == 403