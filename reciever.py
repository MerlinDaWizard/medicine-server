from flask import Flask, request, Request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlalchemy as sa
from typing import Optional

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dispensers.db'
# init db

db = SQLAlchemy(app) # db. = sa. but sa gives annotations

#db.init_app(app)
class Dispensers(db.Model):
    __tablename__ = "dispensers_table"

    id = sa.Column(sa.Integer, primary_key=True)
    passkey = sa.Column(sa.String(10), nullable=False)
    times = db.relationship("ScheduleTimes", backref="dispensers_table")
    latest_connection = sa.Column(sa.DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<name {self.id}>"


class ScheduleTimes(db.Model):
    __tablename__ = "schedule_times_table"

    id = sa.Column(sa.Integer, primary_key=True)
    dispenser_id = sa.Column(sa.Integer, sa.ForeignKey("dispensers_table.id"))
    time = sa.Column(sa.Time, nullable=False)

    def __repr__(self) -> str:
        return f"<name {self.id}>"


def check_login(request: Request) -> Optional[bool]:
    '''Check info provided in request is correct to login'''
    # Check if users request has the dispenser id
    if (str_id := request.values.get('id')) == None:
        return 'No ID provided'

    # Attempt to decode dispenser id to base10 from str hex
    try:
        id = int(str_id,16)
    except:
        return 'Invalid dispenser id format'
    # Check if users request has the passkey
    if (passkey := request.values.get('pass')) == None:
        return 'No pass provided'
    # Check if the dispenser id matches an existing dispenser
    if (dispenser:= db.session.get(Dispensers, id)) == None:
        return 'Invalid dispenser id'
    # Check if the actual dispenser's key matches that provided by the user
    if (dispenser.passkey != passkey):
        return 'Invalid id & passkey combo'

@app.route('/post', methods=['POST'])
def result():
    #con = sl.connect('data.db')
    data = request.form
    data.get('')

@app.route('/times', methods=['POST','GET'])
def times():
    if (err:= check_login(request)) != None:
        return err

    if request.method == 'GET':
        # py 3.8 assign and use
        print(request.values)
        # All success = attempt to 
        return 'success'

    elif request.method == 'POST':
        return 'NYI'


with app.app_context():
    db.create_all()