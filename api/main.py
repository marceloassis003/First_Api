from typing import Optional, Any, Callable, Dict, Generator, Union
from flask import Flask, request, Response, Request, jsonify, make_response, redirect, url_for, render_template
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Join
from pydantic import BaseModel, Field, schema
from pydantic.fields import ModelField
from datetime import datetime
from dataclasses import dataclass
import datetime
import json
from json import encoder, decoder
import pandas as pd
from sqlalchemy_utils import ScalarListType
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash 
import jose
from jose.exceptions import JWTError
from dynaconf import FlaskDynaconf
import jwt



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bd.sqlite"
app.config['JSON_SORT_KEYS'] = False
secret = app.config['SECRET_KEY'] = 'e749a4fd0e4104136484b269a125ddfb'
alg = app.config['JWT_ALGORITHM'] = 'HS256'


db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def to_json(self):
        return{
            "username": self.username, 
            "password": self.password
        }
    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)

# criando classes e tabelas do banco 


class Order(db.Model):
    order_id = db.Column(db.String(255), primary_key=True)
    order_id_mktp = db.Column(db.String(255))
    tracking_number = db.Column(db.String(255))
    sales_channel = db.Column(db.String(255))
    auxiliary_order_ids = db.Column(ScalarListType())
    #auxiliary_order_ids = db.Column(db.ARRAY(db.String(255)))
    order_insertion_date = db.Column(db.String(255)) #db.Column(db.DateTime())

    def __init__(self, order_id, order_id_mktp, tracking_number, sales_channel, auxiliary_order_ids, order_insertion_date):
        self.order_id = order_id 
        self.order_id_mktp = order_id_mktp
        self.tracking_number = tracking_number
        self.sales_channel = sales_channel
        self.auxiliary_order_ids = auxiliary_order_ids
        self.order_insertion_date = order_insertion_date

    def to_json(self):
        return {
            "order_id": self.order_id,
            "order_id_mktp": self.order_id_mktp,
            "tracking_number": self.tracking_number, 
            "sales_channel": self.sales_channel, 
            "auxiliary_order_ids": self.auxiliary_order_ids, 
            "order_insertion_date": self.order_insertion_date
        }


class Invoice(db.Model):
    invoice_number = db.Column(db.Integer, primary_key=True)
    invoice_key = db.Column(db.String(255)) 
    invoice_datetime = db.Column(db.String(255)) 
    invoice_total_value = db.Column(db.Float)

    def __init__(self,invoice_number, invoice_key, invoice_datetime, invoice_total_value):
            self.invoice_number = invoice_number
            self.invoice_key = invoice_key
            self.invoice_datetime = invoice_datetime
            self.invoice_total_value = invoice_total_value

    def to_json(self):
       return {
        "invoice_number": self.invoice_number,
        "invoice_key": self.invoice_key,
        "invoice_datetime": self.invoice_datetime,
        "invoice_total_value": self.invoice_total_value

       } 

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    document = db.Column(db.String(255))
    email = db.Column(db.String(255))
    landline = db.Column(db.String(255))
    cellphone = db.Column(db.String(255))
    additional_telephones = db.Column(ScalarListType())

    def __init__(self, name, document, email, landline, cellphone, additional_telephones):
        self.name = name
        self.document = document
        self.email = email
        self.landline = landline
        self.cellphone = cellphone 
        self.additional_telephones = additional_telephones

    def to_json(self):
       return {
        "name": self.name,
        "document": self.document,
        "email": self.email,
        "landline": self.landline ,
        "cellphone": self.cellphone,
        "additional_telephones": self.additional_telephones

       } 


class Tracking_info(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    courier = db.Column(db.String(255))
    courier_id = db.Column(db.String(255))
    tbx_status_id = db.Column(db.Integer)
    parcel_status = db.Column(db.String(255))
    parcel_substatus = db.Column(db.String(255))
    Events = db.relationship('TrackingEvent', backref='Tracking_info')
   
    

    def __init__(self, courier,courier_id, tbx_status_id, parcel_status, parcel_substatus=None):
        self.courier = courier 
        self.courier_id = courier_id
        self.tbx_status_id = tbx_status_id
        self.parcel_status = parcel_status
        self.parcel_substatus = parcel_substatus
        self.Events = []
    
    def to_json(self):
       event = db.session.query(TrackingEvent).filter(Tracking_info.id == TrackingEvent.tracking_info_id) #db.session.query(TrackingEvent).all()
       return {
        "courier": self.courier,
        "courier_id": self.courier_id,
        "tbx_status_id": self.tbx_status_id,
        "parcel_status": self.parcel_status ,
        "parcel_substatus": self.parcel_substatus,
        "Events": [event.to_json() for event in event]
       }
    
class TrackingEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.Text)
    event_date = db.Column(db.String(255))
    event_site = db.Column(db.String(255))
    trakin_co_link = db.Column(db.String(255))
    tracking_info_id = db.Column(db.Integer, ForeignKey(Tracking_info.id), nullable=False)

    def __init__(self, description, event_date, event_site, trakin_co_link, tracking_info_id):
        self.description = description
        self.event_date = event_date
        self.event_site = event_site
        self.trakin_co_link = trakin_co_link
        self.tracking_info_id = tracking_info_id

    def to_json(self):
       return {
        "description": self.description,
        "event_date": self.event_date,
        "event_site": self.event_site,
        "trakin_co_link": self.trakin_co_link 
       }
    


class Reverse_info(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    authorization_code = db.Column(db.String(255))
    reverse_reason = db.Column(db.String(255))  

    def __init__(self, authorization_code, reverse_reason):
        self.authorization_code = authorization_code
        self.reverse_reason = reverse_reason

    def to_json(self):
       return {
        "authorization_code": self.authorization_code,
        "reverse_reason": self.reverse_reason
       }

# classe que retorna as intancias
class Root():
    def __init__(self, order, invoice, customer, tracking_info, reverse_info):
        self.order = order
        self.invoice = invoice
        self.customer = customer
        self.tracking_info = tracking_info
        self.reverse_info = reverse_info

# classes para documentação Schema 

class Order_spec(BaseModel):
    id: Optional[int]
    order_id_mktp: str
    tracking_number: str
    sales_chanel: str
    auxiliary_order_id: list
    order_insertion_date: str

class Invoice_sche(BaseModel):
    invoice_number: int
    invoice_key: str 
    invoice_datetime: datetime.datetime
    invoice_total_value: float


@app.route("/")
def home():
    return "hello world from api "


@app.route("/about")
def about():
    return "hello abou from this"


if __name__ == "__main__":   
    with app.app_context():
        db.create_all()
    app.run(debug=True)
