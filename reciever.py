from flask import Flask, request, Request, jsonify
from flask.json import JSONEncoder
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,time
import sqlalchemy as sa
from sqlalchemy import orm
from typing import Union
import random

class datetimeJSONEncoder(JSONEncoder):
    def default(self, o):
        if type(o) == time:
            return f'{o.hour:02}' + ':' + f'{o.minute:02}'
        elif type(o) == datetime:
            return o.isoformat(sep=" ")
        else:
            return super().default(o)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dispensers.db'
app.json_encoder = datetimeJSONEncoder
# init db

db = SQLAlchemy(app) # db. = sa. but sa gives annotations

#db.init_app(app)
class Dispenser(db.Model):
    __tablename__ = "dispenser_table"

    id = sa.Column(sa.Integer, primary_key=True)
    passkey = sa.Column(sa.String(10), nullable=False)
    times = db.relationship("ScheduleTime", backref="dispenser_table")
    latest_connection = sa.Column(sa.DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<id {self.id}>"

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class ScheduleTime(db.Model):
    __tablename__ = "schedule_time_table"

    id = sa.Column(sa.Integer, primary_key=True)
    dispenser_id = sa.Column(sa.Integer, sa.ForeignKey("dispenser_table.id"))
    time = sa.Column(sa.Time, nullable=False)

    def __repr__(self) -> str:
        return f"<id {self.id}>"
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
       
def check_login(request: Request) -> Union[Dispenser,str]:
    '''Check info provided in request is correct to login'''
    # Check if users request has the dispenser id
    if (str_id := request.values.get('id')) is None:
        return 'No ID provided', 400
    # Check if users request has the passkey
    if (passkey := request.values.get('pass')) is None:
        return 'No pass provided', 400

    # Attempt to decode dispenser id to base10 from str hex
    try:
        id = int(str_id,16)
    except:
        return 'Invalid dispenser id format', 400
        
    # Check if the dispenser id matches an existing dispenser
    if (dispenser:= db.session.get(Dispenser, id)) is None:
        return 'Invalid dispenser id', 404
    # Check if the actual dispenser's key matches that provided by the user
    if (dispenser.passkey != passkey):
        return 'Invalid id & passkey combo', 404

    return dispenser, None

@app.route('/post', methods=['POST'])
def result():
    #con = sl.connect('data.db')
    data = request.form
    data.get('')

@app.route('/usr', methods=['POST','GET'])
def usr():
    db.session: orm.scoping.scoped_session = db.session # Helps ide autocomplete

    if request.method == 'GET':
        # Returns the latest time for the logged in account
        dispenser_or_err = check_login(request)
        dispenser_or_err, code = check_login(request)
        if code != None: # If it returns a string it is an error to be sent back
            return dispenser_or_err, code
        else:
            dispenser = dispenser_or_err
        return jsonify(dispenser.latest_connection), 200

    elif request.method == 'POST':
        # Generate new account and return data
        # SQL Integer is 4 bytes therefor -2,147,483,648:2,147,483,647 (-2^31 : 2^31 - 1)
        taken = True
        while taken is True:
            id = random.randint(-2_147_483_648,2_147_483_647)
            if db.session.get(Dispenser, id) is None:
                taken = False
        
        passkey = random.randbytes(5)
        print(passkey)
        string_version = passkey.hex()
        print(string_version)
        
        new_dispenser = Dispenser(id=id,passkey=string_version,latest_connection=datetime.now())
        try:
            db.session.add(new_dispenser)
            db.session.commit()
        except:
            return 'database commit failure', 500

        return_data = {'id':f'{id:x}','passkey':string_version}
        return jsonify(return_data)


@app.route('/times', methods=['POST','GET','DELETE'])
def times():
    db.session: orm.scoping.scoped_session = db.session # Helps ide autocomplete
    dispenser_or_err, code = check_login(request)
    if code != None: # If it returns a string it is an error to be sent back
        return dispenser_or_err, code
    else:
        dispenser = dispenser_or_err

    if request.method == 'GET':
        # If its a request from the physical hardware, mark the latest connection in the database
        if request.values.get('type') == 'automatic':
            dispenser.latest_connection = datetime.now() # May be an issue with timezones here
            try:
                db.session.add(dispenser)
                db.session.commit()
            except:
                print("ERROR: cannot commit latest connection info")

        statement = sa.select(ScheduleTime).filter_by(dispenser_id=dispenser.id)
        times = db.session.execute(statement).all()
        #print(type(times))
        times_dict = []
        for t in times:
            temp_dict = t[0].as_dict()
            temp_dict.pop('dispenser_id')
            times_dict.append(temp_dict)
            #print(f"{t[0].id=}")
            #print(f"{t[0].time=}")
        print(times_dict)
        return jsonify(times_dict)

    elif request.method == 'POST':
        if (user_time:= request.values.get('time')) is None:
            return 'No time provided', 400
        try:
            user_time = time.fromisoformat(user_time) # Format = HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]] eg. 04:23:01
        except:
            return 'Invalid time format', 400

        schedule_element = ScheduleTime(dispenser_id=dispenser.id,time=user_time)
        try:
            db.session.add(schedule_element)
            db.session.commit()
        except:
            return 'database commit failure', 500
        return 'success'
    elif request.method == 'DELETE':
        if (del_id:= request.values.get('delid')) is None:
            return 'No time provided', 400
        
        schedule = db.session.get(ScheduleTime, del_id)
        if schedule and schedule.dispenser_id == dispenser.id:
            try:
                db.session.delete(schedule)
                db.session.commit()
            except:
                return 'database commit failure', 500
            return 'success', 200
        else:
            return 'Can\'t find time with that key', 404


with app.app_context():
    db.create_all()