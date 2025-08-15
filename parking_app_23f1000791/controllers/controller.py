from flask import Flask, render_template, url_for, redirect, request, flash, session
from flask import current_app as app
from models.models import *
from datetime import datetime

@app.route("/")
def home():
    return render_template('home.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        pwd = request.form["pwd"]

        u = User.query.filter_by(username=username).first()

        if u and u.password == pwd:
            
            session['user_id'] = u.id
            session['username'] = u.username
            session['role'] = u.role

            if u.role == "admin":
                flash('Admin login successful!')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login successful!')
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password!')

    return render_template('login.html')



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['pwd']
        email = request.form['email']


        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Username already exists!')
        elif existing_email:
            flash('Email already registered!')
        else:
            
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)

            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))    


    return render_template('register.html')

@app.route('/admin')
def admin_dashboard():
    
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin login required.')
        return redirect(url_for('login'))


    all_users = User.query.all()
    all_lots = Parking_lot.query.all()
    all_spots = Spots.query.all()
    occupied = Spots.query.filter_by(status='O').count()
    available = Spots.query.filter_by(status='A').count()

    return render_template('admin_dashboard.html',
                             users=all_users,
                             lots=all_lots,
                             occupied_spots=occupied,
                             available_spots=available,
                             current_year=datetime.now().year)


@app.route("/add_parking_lot", methods=['GET', 'POST'])
def add_parking_lot():

    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin login required.')
        return redirect(url_for('login'))

    if request.method == 'POST':

        name = request.form['name']
        location = request.form['location']
        address = request.form['address']
        pincode = request.form['pincode']
        price = float(request.form['price'])
        max_spots = int(request.form['max_spots'])

            
        lot = Parking_lot(name=name, location=location, address=address, 
                            pincode=pincode, price=price, max_spots=max_spots)
        db.session.add(lot)
        db.session.flush()  

        for i in range(1, max_spots + 1):
            spot = Spots(lot_id=lot.id, spot_number=i)
            db.session.add(spot)

        db.session.commit()
        flash('Parking lot created successfully!')
        return redirect(url_for('admin_dashboard'))



    return render_template('add_parking_lot.html')

@app.route('/edit_parking_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_parking_lot(lot_id):
    
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin login required.')
        return redirect(url_for('login'))

    lot = Parking_lot.query.get_or_404(lot_id)

    if request.method == 'POST':

        name = request.form['name']
        location = request.form['location']
        address = request.form['address']
        pincode = request.form['pincode']
        price = float(request.form['price'])
        new_max_spots = int(request.form['max_spots'])
            
            
        old_max_spots = lot.max_spots
        if new_max_spots > old_max_spots: 

            for i in range(old_max_spots + 1, new_max_spots + 1):
                spot = Spots(lot_id=lot.id, spot_number=i)
                db.session.add(spot)

        elif new_max_spots < old_max_spots:
            spots = Spots.query.filter_by(lot_id=lot.id).all()
            for spot in spots:
                if spot.status == 'O':
                    flash('Cannot reduce spots: Some spots are occupied!')
                    return render_template('edit_parking_lot.html', lot=lot)
                else:
                    if spot.spot_number>new_max_spots:
                        db.session.delete(spot)

            
        lot.name = name
        lot.location = location
        lot.address = address
        lot.pincode = pincode
        lot.price = price 
        lot.max_spots = new_max_spots
        db.session.commit()
        flash('Parking lot updated successfully!')
        return redirect('/admin')

       

    return render_template('edit_parking_lot.html', lot=lot)


@app.route('/delete_parking_lot/<int:lot_id>')
def delete_parking_lot(lot_id):
    
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin login required.')
        return redirect(url_for('login'))


    lot = Parking_lot.query.get_or_404(lot_id)
    count = Spots.query.filter_by(lot_id=lot_id).count()
        
    occupied_spots = Spots.query.filter_by(lot_id=lot_id, status='O').count()
    if occupied_spots > 0:
        flash('Cannot delete parking lot! Some spots are still occupied.')
    else:
        db.session.delete(lot)


        db.session.commit()
        flash('Parking lot deleted successfully!')


    return redirect(url_for('admin_dashboard'))

@app.route('/view_parking_lot/<int:lot_id>')
def view_parking_lot(lot_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin login required.')
        return redirect('/login')
    lot = Parking_lot.query.get_or_404(lot_id)
    spots = Spots.query.filter_by(lot_id=lot_id).all()

    return render_template('view_parking_lot.html',spots=spots,lot=lot)
    
    

    return render_template('view_parking_lot.html', spots=spots,lot=lot)



@app.route('/user')
def user_dashboard():

    if 'user_id' not in session:
        flash("Please log in to access the user dashboard.")
        return redirect(url_for('login'))

    if session.get('role') == 'admin':
        flash("Admin cannot access user dashboard.")
        return redirect(url_for('admin_dashboard'))


    user_id = session['user_id']
    user = User.query.get(user_id)

    if not user:
        flash("User does not exist. Please log in again.")
        session.clear()
        return redirect(url_for('login'))


    lots = Parking_lot.query.all()


    current_reservations = db.session.query(
            Reservations.id,
            Reservations.start_time,
            Reservations.end_time,
            Reservations.cost,
            Parking_lot.name,
            Spots.spot_number
        ).join(Spots, Reservations.spot_id == Spots.id) \
         .join(Parking_lot, Spots.lot_id == Parking_lot.id) \
         .filter(
            Reservations.user_id == user_id,
            Reservations.end_time.is_(None)  
         ) \
         .order_by(Reservations.start_time) \
         .all()


    past_reservations = db.session.query(
            Reservations.id,
            Reservations.start_time,
            Reservations.end_time,
            Reservations.cost,
            Parking_lot.name,
            Spots.spot_number
        ).join(Spots, Reservations.spot_id == Spots.id) \
         .join(Parking_lot, Spots.lot_id == Parking_lot.id) \
         .filter(
            Reservations.user_id == user_id,
            Reservations.end_time.isnot(None)  
         ) \
         .order_by(Reservations.end_time) \
         .limit(5) \
         .all()

    return render_template('user_dashboard.html',
                             user=user,
                             lots=lots,
                             current_reservations=current_reservations,
                             history=past_reservations,
                             current_year=datetime.now().year)



@app.route('/book_parking/<int:lot_id>', methods=['GET', 'POST'])
def book_parking(lot_id):

    if 'user_id' not in session:
        flash("Please log in to book parking.")
        return redirect(url_for('login'))


    lot = Parking_lot.query.get_or_404(lot_id)
    user_id = session['user_id']


    active_reservation = Reservations.query.filter_by(
            user_id=user_id, 
            end_time=None
        ).first()

    if active_reservation:
        flash('You already have an active parking reservation!')
        return redirect(url_for('user_dashboard'))


    available_spot = Spots.query.filter_by(
            lot_id=lot_id, 
            status='A'
        ).first()

    if not available_spot:
        flash('No available spots in this parking lot!')
        return redirect(url_for('user_dashboard'))


    reservation = Reservations(
            spot_id=available_spot.id,
            user_id=user_id,
            start_time=datetime.utcnow(),
            cost=0.0  
        )

    available_spot.status = 'O'

    db.session.add(reservation)
    db.session.commit()

    flash(f'Parking booked successfully! Spot {available_spot.spot_number}')
    return redirect(url_for('user_dashboard'))



@app.route('/checkout/<int:reservation_id>')
def checkout(reservation_id):

    if 'user_id' not in session:
        flash("Please log in to checkout.")
        return redirect(url_for('login'))

    user_id = session['user_id']
    reservation = Reservations.query.filter_by(
            id=reservation_id, 
            user_id=user_id,
            end_time=None
        ).first()

    if not reservation:
        flash('Invalid reservation or already checked out!')
        return redirect(url_for('user_dashboard'))


    end_time = datetime.utcnow()
    duration_hours = (end_time - reservation.start_time).total_seconds() / 3600


    spot = Spots.query.get(reservation.spot_id)
    lot = Parking_lot.query.get(spot.lot_id)


    hours_to_charge = max(1, duration_hours)
    total_cost = hours_to_charge * lot.price


    reservation.end_time = end_time
    reservation.cost = total_cost


    spot.status = 'A'

    db.session.commit()

    flash(f'Checkout successful! Total cost: ₹{total_cost:.2f}')
    return redirect(url_for('user_dashboard'))



@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))
