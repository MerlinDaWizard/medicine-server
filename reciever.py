from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlalchemy as sa
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


subscribers = []

@app.route('/post', methods=['POST'])
def result():
    #con = sl.connect('data.db')
    data = request.form
    data.get('')

@app.route('/times', methods=['POST','GET'])
def times():
    if request.method == 'GET':
        # py 3.8 assign and use
        print(request.values)
        if (str_id := request.values.get('id')) == None:
            return 'No ID provided'

        try:
            id = int(str_id,16)
        except:
            return 'Invalid dispenser id format'

        if (passkey := request.values.get('pass')) == None:
            return 'No pass provided'
        
        ### Error because db.session.get refers to the `schedule_times_table` instead of the main `dispensers_table`
        if (dispenser:= db.session.get(Dispensers, id)) == None:
            return 'Invalid dispenser id'
        
        if (dispenser.passkey != passkey):
            return 'Invalid id & passkey combo'
        
        return 'success'

    elif request.method == 'POST':
        return 'NYI'


with app.app_context():
    db.create_all()