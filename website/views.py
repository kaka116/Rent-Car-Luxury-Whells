from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import Vehicles, Reservations, db, Payments
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
import random
import json
import os

# Create a Blueprint for views
views = Blueprint('views', __name__)


# Routes for website pages


@views.route('/')
@login_required
def home():
    vehicles = Vehicles.query.all()
    current_date = datetime.now().date()  # Get the current date
    random_reference = random.randint(100000000, 999999999)
    reserve = Reservations.query.all()

    # Calculate next inspection date for each vehicle
    for vehicle in vehicles:
        vehicle.next_inspection = vehicle.last_inspection + relativedelta(years=1)

    unavailable_dates_vehicle = {}

    # Get unavailable dates for each vehicle
    for vehicle in vehicles:
        vehicle_id = vehicle.id
        unavailable_dates_vehicle[vehicle_id] = []

        for date_str in vehicle.reserve_dates:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            unavailable_dates_vehicle[vehicle_id].append(date_obj)

    unavailable_dates_by_vehicle = {}

    for vehicle_id, dates in unavailable_dates_vehicle.items():
        filtered_dates = [date for date in dates if date >= current_date]
        unavailable_dates_by_vehicle[vehicle_id] = filtered_dates

    return render_template(
        "home.html", user=current_user, vehicles=vehicles, current_date=current_date,
        random_reference=random_reference, reserve=reserve, unavailable_dates_by_vehicle=unavailable_dates_by_vehicle
    )


# Route to create a new reservation


@views.route('/create_reservations', methods=['POST'])
@login_required
def create_reservations():
    data = request.get_json()
    user_id = current_user.id
    vehicle_id = data.get('vehicle_id')
    vehicle_model = data.get('vehicle_model')
    vehicle_price_day = data.get('vehicle_price_day')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    total = data.get('total')

    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

    reservation_id = None

    existing_reservation = Reservations.query.filter_by(vehicle_id=vehicle_id).filter(
        (Reservations.start_date <= end_date_obj) & (Reservations.end_date >= start_date_obj) &
        (Reservations.refund == False)
    ).first()

    if existing_reservation:
        # Edit existing reservation
        existing_reservation.start_date = start_date_obj
        existing_reservation.end_date = end_date_obj
        existing_reservation.total = total
        db.session.commit()
        reservation_id = existing_reservation.id

    else:
        # Create New reservation
        new_reservation = Reservations(
            user_id=user_id,
            vehicle_id=vehicle_id,
            vehicle_model=vehicle_model,
            vehicle_price_day=vehicle_price_day,
            start_date=start_date_obj,
            end_date=end_date_obj,
            total=total,
            pay_confirmation=False,
            payment_receipt='',
            refund=False
        )
        db.session.add(new_reservation)
        db.session.commit()
        reservation_id = new_reservation.id

    vehicle = Vehicles.query.get(vehicle_id)

    if not vehicle:
        return jsonify({'status': 'error', 'message': 'Vehicle not found'}), 404

    # Add reserved dates to the vehicle
    current_date = start_date_obj
    while current_date <= end_date_obj:
        vehicle.reserve_dates = vehicle.reserve_dates + [current_date.strftime('%Y-%m-%d')]
        current_date += timedelta(days=1)

    db.session.commit()
    return jsonify(
        {'status': 'success', 'message': 'New Reservation Created!', 'reservation_id': reservation_id}), 200


# Route to show reservations


@views.route('/reservations', methods=['GET'])
@login_required
def reservations():
    random_reference = random.randint(100000000, 999999999)
    user_reservations = Reservations.query.filter_by(user_id=current_user.id).all()
    vehicles = Vehicles.query.all()
    # If you want to try different current dates /reservations page
    # current_date = datetime.strptime("2030-01-01", "%Y-%m-%d").date()

    current_date = datetime.now().date()
    disable_refund_day = None

    # Get future reservations
    new_reservations = [reservation for reservation in user_reservations if reservation.start_date > current_date]
    for reservation in new_reservations:
        start_date_obj = reservation.start_date
        disable_refund_day = start_date_obj - timedelta(days=2)

    unavailable_dates_vehicle = {}

    # Get unavailable dates for each vehicle
    for vehicle in vehicles:
        vehicle_id = vehicle.id
        unavailable_dates_vehicle[vehicle_id] = []

        for date_str in vehicle.reserve_dates:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            unavailable_dates_vehicle[vehicle_id].append(date_obj)
            vehicle.reserve_dates = vehicle.reserve_dates or []

    unavailable_dates_by_vehicle = {}

    for vehicle_id, dates in unavailable_dates_vehicle.items():
        filtered_dates = [date for date in dates if date >= current_date]
        unavailable_dates_by_vehicle[vehicle_id] = filtered_dates

    return render_template("reservations.html", user=current_user, reservations=new_reservations,
                           current_date=current_date, disable_refund_day=disable_refund_day, vehicle=vehicles,
                           unavailable_dates_by_vehicle=unavailable_dates_by_vehicle, random_reference=random_reference)


# Route to show reservation history
@views.route('/reservations_history', methods=['GET'])
@login_required
def reservations_history():
    user_reservations = Reservations.query.filter_by(user_id=current_user.id).all()
    current_date = datetime.now().date()

    # Get past reservations
    old_reservations = [reservation for reservation in user_reservations if reservation.start_date < current_date]

    return render_template("reservations_history.html", user=current_user, reservations=old_reservations)


# Route to create a payment


@views.route('/create_payment', methods=['POST'])
@login_required
def create_payment():
    data = request.get_json()
    user_id = current_user.id
    reserve_id = data.get('reserve_id')
    entity = data.get('entity')
    reference = data.get('reference')
    amount = data.get('amount')

    new_payment = Payments(
        user_id=user_id,
        reservation_id=reserve_id,
        entity=entity,
        reference=reference,
        amount=amount)

    db.session.add(new_payment)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Payment Registered!'}), 200


# Route to delete a reservation


@views.route('/delete_reservation', methods=['POST'])
@login_required
def delete_reservation():
    dl_reservation = json.loads(request.data)
    reservation_id = dl_reservation['reservation_id']
    dl_reservation = Reservations.query.get(reservation_id)
    vehicle = Vehicles.query.get(dl_reservation.vehicle_id)

    if dl_reservation:
        if dl_reservation.user_id == current_user.id:
            for payment in dl_reservation.reservations_payment:
                db.session.delete(payment)
            db.session.delete(dl_reservation)
            db.session.commit()

    start_date = dl_reservation.start_date
    end_date = dl_reservation.end_date

    # Remove reserved dates from vehicle
    while start_date <= end_date:
        date_str = start_date.strftime("%Y-%m-%d")
        if date_str in vehicle.reserve_dates:
            vehicle.reserve_dates = [date for date in vehicle.reserve_dates if date != date_str]
        start_date += timedelta(days=1)

    db.session.commit()

    return jsonify({"success": True, "message": "Reservation deleted!"})


# Route to confirm payment


@views.route('/confirm_payment', methods=['POST'])
@login_required
def confirm_payment():
    conf_pay = json.loads(request.data)
    reservation_id = conf_pay.get('reservation_id')
    reservation = Reservations.query.get(reservation_id)

    if reservation and reservation.user_id == current_user.id:
        reservation.pay_confirmation = True
        db.session.commit()
        return jsonify({"success": True, "message": "Payment confirmed!"})

    return jsonify({"success": False, "message": "Reservation not found or unauthorized."}), 400


# Route to upload a payment receipt


@views.route('/payment_receipt', methods=['POST'])
@login_required
def payment_receipt():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file was sent."})

    file = request.files['file']

    if file.filename == '':
        return jsonify({"success": False, "message": "Empty file."})
    # Get reservation ID from the form
    reservation_id = request.form.get('reservation_id')
    reservation = Reservations.query.get(reservation_id)

    if not reservation_id:
        return jsonify({"success": False, "message": "Reservation ID is missing."})

    receipt_folder = os.path.join("instance", "payment_receipt")
    os.makedirs(receipt_folder, exist_ok=True)
    filename = f"reservation_{reservation_id}_{secure_filename(file.filename)}"
    file.save(os.path.join(receipt_folder, filename))

    # If the current user is the owner of the reservation, save the file path in the reservation
    if reservation.user_id == current_user.id:
        reservation.payment_receipt = f'instance/payment_receipt/{filename}'
        db.session.commit()
        return jsonify({"success": True, "message": "Receipt added!"})

    return jsonify({"success": True, "message": "File received successfully!"})


# Route to refund a reservation


@views.route('/refund_reservation', methods=['POST'])
@login_required
def refund():
    # Get the reservation ID from the request
    rf_reservation = json.loads(request.data)
    reservation_id = rf_reservation['reservation_id']
    reservation = Reservations.query.get(reservation_id)
    vehicle = Vehicles.query.get(reservation.vehicle_id)

    # If the reservation exists and the current user is the owner
    if reservation:
        if reservation.user_id == current_user.id:
            reservation.refund = True
            db.session.commit()

    # Remove reserved dates from the vehicle
    start_date = reservation.start_date
    end_date = reservation.end_date

    while start_date <= end_date:

        date_str = start_date.strftime("%Y-%m-%d")
        if date_str in vehicle.reserve_dates:
            vehicle.reserve_dates = [date for date in vehicle.reserve_dates if date != date_str]
        start_date += timedelta(days=1)

    db.session.commit()

    return jsonify({"success": True, "message": "Reservation refunded!"})


@views.route('/edit_reservation', methods=['POST'])
@login_required
def edit_reservation():
    edt_reservation = json.loads(request.data)
    reservation_id = edt_reservation['reservation_id']
    edt_reservation = Reservations.query.get(reservation_id)
    vehicle = Vehicles.query.get(edt_reservation.vehicle_id)

    # falta o codigo para remover o pagamento associado á reserva
    if edt_reservation:
        if edt_reservation.user_id == current_user.id:
            for payment in edt_reservation.reservations_payment:
                db.session.delete(payment)
                db.session.commit()
    start_date = edt_reservation.start_date
    end_date = edt_reservation.end_date

    # Remove reserved dates from vehicle
    while start_date <= end_date:
        date_str = start_date.strftime("%Y-%m-%d")
        if date_str in vehicle.reserve_dates:
            vehicle.reserve_dates = [date for date in vehicle.reserve_dates if date != date_str]
        start_date += timedelta(days=1)

    db.session.commit()

    return jsonify({"success": True, "message": "Edit Reservation!"})
