from flask import Flask, request, Request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,time
import sqlalchemy as sa
from typing import Union

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dispensers.db'
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
        return f"<name {self.id}>"


class ScheduleTime(db.Model):
    __tablename__ = "schedule_time_table"

    id = sa.Column(sa.Integer, primary_key=True)
    dispenser_id = sa.Column(sa.Integer, sa.ForeignKey("dispenser_table.id"))
    time = sa.Column(sa.Time, nullable=False)

    def __repr__(self) -> str:
        return f"<name {self.id}>"


def check_login(request: Request) -> Union[Dispenser,str]:
    '''Check info provided in request is correct to login'''
    # Check if users request has the dispenser id
    if (str_id := request.values.get('id')) is None:
        return 'No ID provided'
    # Check if users request has the passkey
    if (passkey := request.values.get('pass')) is None:
        return 'No pass provided'

    # Attempt to decode dispenser id to base10 from str hex
    try:
        id = int(str_id,16)
    except:
        return 'Invalid dispenser id format'
        
    # Check if the dispenser id matches an existing dispenser
    if (dispenser:= db.session.get(Dispenser, id)) is None:
        return 'Invalid dispenser id'
    # Check if the actual dispenser's key matches that provided by the user
    if (dispenser.passkey != passkey):
        return 'Invalid id & passkey combo'

    return dispenser

@app.route('/post', methods=['POST'])
def result():
    #con = sl.connect('data.db')
    data = request.form
    data.get('')

@app.route('/times', methods=['POST','GET'])
def times():
    dispenser_or_err = check_login(request)
    if type(dispenser_or_err) is str: # If it returns a string it is an error to be sent back
        return dispenser_or_err
    else:
        dispenser = dispenser_or_err

    if request.method == 'GET':
        # py 3.8 assign and use
        print(request.values)
        return 'success'

    elif request.method == 'POST':
        if (user_time:= request.values.get('time')) is None:
            return 'No time provided.'
        try:
            user_time = time.fromisoformat(user_time) # Format = HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]] eg. 04:23:01
        except:
            return 'Invalid time format'

        schedule_element = ScheduleTime(dispenser_id=dispenser.id,time=user_time)
        #try:
        db.session.add(schedule_element)
        db.session.commit()
        #except:
        #    return 'database commit failure'
        return 'POST success'


with app.app_context():
    db.create_all()