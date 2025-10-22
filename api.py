from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, marshal, abort
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

# ======================================
# Auxiliary methods
# ======================================


def str_to_date(value, name):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"{name} must be in YYYY-MM-DD format")


def str_to_time(value, name):
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        raise ValueError(f"{name} must be in HH:MM format")


def format_date(reservation):
    return reservation.reservation_date.strftime("%Y-%m-%d")


def format_time(time_obj):
    return time_obj.strftime("%H:%M")


# ======================================
# Models
# ======================================

class MeetingRoomModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"MeetingRoom(name = {self.name})"


class RoomReservationModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey(
        'meeting_room_model.id'), nullable=False)
    reservation_date = db.Column(db.Date, nullable=False)
    start_hour = db.Column(db.Time, nullable=False)
    end_hour = db.Column(db.Time, nullable=False)

    room = db.relationship(
        "MeetingRoomModel", backref=db.backref("reservations", lazy=True))

    def __repr__(self):
        return f"<RoomReservation id={self.id} room_id={self.room_id}>"

# ======================================
# Parsers
# ======================================


meeting_room_args = reqparse.RequestParser()
meeting_room_args.add_argument(
    'name', type=str, required=True, help="Meeting room name cannot be blank")

room_reservation_args = reqparse.RequestParser()
room_reservation_args.add_argument(
    'room_name', type=str, required=True, help="Meeting room name cannot be blank")
room_reservation_args.add_argument(
    'reservation_date',  type=lambda x: str_to_date(x, 'reservation_date'), required=True)
room_reservation_args.add_argument(
    'start_hour', type=lambda x: str_to_time(x, 'start_hour'), required=True)
room_reservation_args.add_argument(
    'end_hour', type=lambda x: str_to_time(x, 'end_hour'), required=True)


update_room_reservation_args = reqparse.RequestParser()
update_room_reservation_args.add_argument(
    'reservation_date', type=lambda x: str_to_date(x, 'reservation_date'), required=True
)
update_room_reservation_args.add_argument(
    'start_hour', type=lambda x: str_to_time(x, 'start_hour'), required=True
)
update_room_reservation_args.add_argument(
    'end_hour', type=lambda x: str_to_time(x, 'end_hour'), required=True
)

# ======================================
# Endpoints
# ======================================

meetingRoomFields = {
    'id': fields.Integer,
    'name': fields.String,
}

roomReservationFields = {
    'id': fields.Integer,
    'room_name': fields.String(attribute=lambda x: x.room.name),
    'reservation_date': fields.String(attribute=lambda x: format_date(x)),
    'start_hour': fields.String(attribute=lambda x: format_time(x.start_hour)),
    'end_hour': fields.String(attribute=lambda x: format_time(x.end_hour)),
}


class MeetingRooms(Resource):
    @marshal_with(meetingRoomFields)
    def get(self):
        meeting_rooms = MeetingRoomModel.query.all()
        return meeting_rooms

    @marshal_with(meetingRoomFields)
    def post(self):
        args = meeting_room_args.parse_args()
        meeting_room = MeetingRoomModel(name=args["name"])
        db.session.add(meeting_room)
        db.session.commit()
        meeting_rooms = MeetingRoomModel.query.all()
        return meeting_rooms, 201


class RoomReservations(Resource):
    @marshal_with(roomReservationFields)
    def get(self):
        room_reservations = RoomReservationModel.query.all()
        return room_reservations

    def post(self):
        args = room_reservation_args.parse_args()

        if args["start_hour"] >= args["end_hour"]:
            return {"error": "Start hour must be earlier than end hour"}, 400

        room = MeetingRoomModel.query.filter_by(name=args["room_name"]).first()
        if not room:
            return {"error": "Meeting room does not exist"}, 404

        overlapping = RoomReservationModel.query.filter(
            RoomReservationModel.room_id == room.id,
            RoomReservationModel.reservation_date == args["reservation_date"],
            RoomReservationModel.start_hour < args["end_hour"],
            RoomReservationModel.end_hour > args["start_hour"]
        ).first()
        if overlapping:
            return {"error": "Time slot already reserved"}, 409

        room_reservation = RoomReservationModel(
            room_id=room.id,
            reservation_date=args["reservation_date"],
            start_hour=args["start_hour"],
            end_hour=args["end_hour"])
        db.session.add(room_reservation)
        db.session.commit()

        room_reservations = RoomReservationModel.query.all()
        return marshal(room_reservations, roomReservationFields), 201


class RoomReservation(Resource):
    @marshal_with(roomReservationFields)
    def get(self, id):
        reservation = RoomReservationModel.query.filter_by(id=id).first()
        if not reservation:
            abort(404, description="Room reservation not found")
        return reservation

    @marshal_with(roomReservationFields)
    def put(self, id):
        args = update_room_reservation_args.parse_args()
        reservation = RoomReservationModel.query.filter_by(id=id).first()

        if not reservation:
            abort(404, description="Room reservation not found")

        if args["start_hour"] >= args["end_hour"]:
            return {"error": "Start hour must be earlier than end hour"}, 400

        overlapping = RoomReservationModel.query.filter(
            RoomReservationModel.room_id == reservation.room_id,
            RoomReservationModel.id != reservation.id,
            RoomReservationModel.reservation_date == args["reservation_date"],
            RoomReservationModel.start_hour < args["end_hour"],
            RoomReservationModel.end_hour > args["start_hour"]
        ).first()
        if overlapping:
            return {"error": "Time slot already reserved"}, 409

        reservation.reservation_date = args["reservation_date"]
        reservation.start_hour = args["start_hour"]
        reservation.end_hour = args["end_hour"]

        db.session.commit()
        return reservation, 200

    def delete(self, id):
        reservation = RoomReservationModel.query.filter_by(id=id).first()
        if not reservation:
            abort(404, description="Room reservation not found")
        db.session.delete(reservation)
        db.session.commit()
        return '', 204


api.add_resource(MeetingRooms, '/meetingrooms/')
api.add_resource(RoomReservations, '/reservations/')
api.add_resource(RoomReservation, '/reservations/<int:id>')


@app.route('/')
def home():
    return 'Homepage'


if __name__ == '__main__':
    app.run(debug=True)
