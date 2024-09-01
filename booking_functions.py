import mysql.connector
import os
import bcrypt
import hashlib
from datetime import datetime 

user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
database = os.getenv("MYSQL_DATABASE")

def connect_to_db():
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

def check_availability_flight(db_connection, flight_id):
    cursor = db_connection.cursor()
    query = "SELECT Availability FROM Flight WHERE FlightID = %s"
    cursor.execute(query, (flight_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else 0

def check_availability_hotel(db_connection, hotel_id):
    cursor = db_connection.cursor()
    query = "SELECT Availability FROM Hotel WHERE HotelID = %s"
    cursor.execute(query, (hotel_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else 0

def check_availability_car(db_connection, car_id):
    cursor = db_connection.cursor()
    query = "SELECT Availability FROM Car WHERE CarID = %s"
    cursor.execute(query, (car_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else 0

def custom_hash(booking_id):
    # Using the common substring in the roll numbers
    prefix = "B22AI"
    combined = prefix + str(booking_id)
    hash_value = hash(combined)
    
    # Limit the hash value to a certain range, for example, 1000 buckets
    return hash_value % 1000

def make_booking(db_connection, user_id, booking_date, total_amount, flight_id=None, hotel_id=None, car_id=None):
    cursor = db_connection.cursor()

    # Check availability for each service
    if flight_id and check_availability_flight(db_connection, flight_id) < 1:
        return "Flight not available"
    if hotel_id and check_availability_hotel(db_connection, hotel_id) < 1:
        return "Hotel not available"
    if car_id and check_availability_car(db_connection, car_id) < 1:
        return "Car not available"

    # Create booking creation time
    creation_time = datetime.now()

    # Insert booking with creation time (booking hash will be updated later)
    insert_query = """
    INSERT INTO Booking (UserID, BookingDate, TotalAmount, BookingCreationTime)
    VALUES (%s, %s, %s, %s);
    """
    cursor.execute(insert_query, (user_id, booking_date, total_amount, creation_time))
    booking_id = cursor.lastrowid

    # Generate the custom hash based on the booking ID
    booking_hash = custom_hash(booking_id)

    # Update the booking record with the custom hash value
    cursor.execute("UPDATE Booking SET BookingHash = %s WHERE BookingID = %s", (booking_hash, booking_id))

    # Update availability and link to booking
    if flight_id:
        cursor.execute("UPDATE Flight SET Availability = Availability - 1 WHERE FlightID = %s", (flight_id,))
        cursor.execute("INSERT INTO BookingFlight (BookingID, FlightID) VALUES (%s, %s)", (booking_id, flight_id))
    if hotel_id:
        cursor.execute("UPDATE Hotel SET Availability = Availability - 1 WHERE HotelID = %s", (hotel_id,))
        cursor.execute("INSERT INTO BookingHotel (BookingID, HotelID) VALUES (%s, %s)", (booking_id, hotel_id))
    if car_id:
        cursor.execute("UPDATE Car SET Availability = Availability - 1 WHERE CarID = %s", (car_id,))
        cursor.execute("INSERT INTO BookingCar (BookingID, CarID) VALUES (%s, %s)", (booking_id, car_id))

    db_connection.commit()
    cursor.close()
    return "Booking successful"

def view_available_flights(db_connection, departure_city, arrival_city, departure_date):
    cursor = db_connection.cursor()
    query = """
    SELECT * FROM Flight
    WHERE DepartureCity = %s AND ArrivalCity = %s AND DepartureDate = %s AND Availability > 0
    """
    cursor.execute(query, (departure_city, arrival_city, departure_date))
    result = cursor.fetchall()
    cursor.close()
    return result

def view_available_hotels(db_connection, city, checkin_date):
    cursor = db_connection.cursor()
    query = """
    SELECT * FROM Hotel
    WHERE City = %s AND Availability > 0
    """
    cursor.execute(query, (city,))
    result = cursor.fetchall()
    cursor.close()
    return result

def view_available_cars(db_connection, city, rental_date):
    cursor = db_connection.cursor()
    query = """
    SELECT * FROM Car
    WHERE City = %s AND Availability > 0
    """
    cursor.execute(query, (city,))
    result = cursor.fetchall()
    cursor.close()
    return result

def filter_flights(db_connection, departure_city, arrival_city, date_range):
    cursor = db_connection.cursor()
    query = """
    SELECT * FROM Flight
    WHERE DepartureCity = %s AND ArrivalCity = %s AND DepartureDate BETWEEN %s AND %s
    """
    cursor.execute(query, (departure_city, arrival_city, date_range[0], date_range[1]))
    result = cursor.fetchall()
    cursor.close()
    return result


def get_user_bookings(db_connection, user_id):
    cursor = db_connection.cursor()
    
    # Query to get bookings
    query = """
    SELECT 
        Booking.BookingID, 
        Booking.BookingDate, 
        Booking.TotalAmount
    FROM Booking
    WHERE Booking.UserID = %s
    """
    cursor.execute(query, (user_id,))
    bookings = cursor.fetchall()
    
    # Fetch associated FlightID, HotelID, and CarID for each booking
    detailed_bookings = []
    for booking in bookings:
        booking_id = booking[0]
        
        # Retrieve FlightID
        cursor.execute("SELECT FlightID FROM BookingFlight WHERE BookingID = %s", (booking_id,))
        flight_id = cursor.fetchone()
        flight_id = flight_id[0] if flight_id else None

        # Retrieve HotelID
        cursor.execute("SELECT HotelID FROM BookingHotel WHERE BookingID = %s", (booking_id,))
        hotel_id = cursor.fetchone()
        hotel_id = hotel_id[0] if hotel_id else None

        # Retrieve CarID
        cursor.execute("SELECT CarID FROM BookingCar WHERE BookingID = %s", (booking_id,))
        car_id = cursor.fetchone()
        car_id = car_id[0] if car_id else None
        
        # Add the full details to the list
        detailed_bookings.append((booking_id, booking[1], booking[2], flight_id, hotel_id, car_id))
    
    cursor.close()
    return detailed_bookings



def verify_user_login(db_connection, email, password):
    cursor = db_connection.cursor()
    query = "SELECT UserID, Password FROM User WHERE Email = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        stored_user_id, stored_password = result
        if password == stored_password:  # Direct comparison (update this if you start hashing passwords)
            return stored_user_id
    return None

def is_admin(email, password):
    # Hardcoded admin credentials
    admin_email = "admin@example.com"
    admin_password = "admin123"  # This should be hashed for security

    return email == admin_email and password == admin_password

def view_all_users(db_connection):
    cursor = db_connection.cursor()
    query = "SELECT UserID, Name, Email, ContactNumber FROM User"
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    return users

def view_user_bookings(db_connection):
    cursor = db_connection.cursor()
    query = """
    SELECT Booking.BookingID, User.Name, Booking.BookingDate, Booking.TotalAmount, Booking.BookingCreationTime
    FROM Booking
    JOIN User ON Booking.UserID = User.UserID
    """
    cursor.execute(query)
    bookings = cursor.fetchall()
    cursor.close()
    return bookings
    
def add_travel_option(db_connection, option_type, details):
    cursor = db_connection.cursor()

    if option_type == "flight":
        query = """
        INSERT INTO Flight (FlightNumber, DepartureCity, ArrivalCity, DepartureDate, ArrivalDate, Price, Availability)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
    elif option_type == "hotel":
        query = """
        INSERT INTO Hotel (Name, City, CheckInDate, CheckOutDate, PricePerNight, Availability)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
    elif option_type == "car":
        query = """
        INSERT INTO Car (Model, City, RentalDate, PricePerDay, Availability)
        VALUES (%s, %s, %s, %s, %s)
        """
    else:
        cursor.close()
        return "Invalid option type"

    cursor.execute(query, details)
    db_connection.commit()
    cursor.close()

    return f"{option_type.capitalize()} added successfully"

def view_all_flights(db_connection):
    cursor = db_connection.cursor()
    query = "SELECT * FROM Flight"
    cursor.execute(query)
    flights = cursor.fetchall()
    cursor.close()
    return flights

def view_all_hotels(db_connection):
    cursor = db_connection.cursor()
    query = "SELECT * FROM Hotel"
    cursor.execute(query)
    hotels = cursor.fetchall()
    cursor.close()
    return hotels

def view_all_cars(db_connection):
    cursor = db_connection.cursor()
    query = "SELECT * FROM Car"
    cursor.execute(query)
    cars = cursor.fetchall()
    cursor.close()
    return cars

def create_user_account(db_connection, name, email, password, contact_number, creation_time):
    cursor = db_connection.cursor()
    
    # SQL query to insert the new user into the User table
    insert_user_query = """
    INSERT INTO User (Name, Email, Password, ContactNumber, CreationTime)
    VALUES (%s, %s, %s, %s, %s);
    """
    
    # Execute the query with the provided data
    cursor.execute(insert_user_query, (name, email, password, contact_number, creation_time))
    
    # Commit the transaction to save the data
    db_connection.commit()
    
    # Close the cursor
    cursor.close()
    
    return "Account created successfully"

def remove_booking(db_connection, booking_id, user_id):
    cursor = db_connection.cursor()
    
    # Check if the booking belongs to the user
    check_query = "SELECT BookingID FROM Booking WHERE BookingID = %s AND UserID = %s"
    cursor.execute(check_query, (booking_id, user_id))
    result = cursor.fetchone()

    if result:
        # If the booking belongs to the user, proceed to delete
        delete_booking_query = "DELETE FROM Booking WHERE BookingID = %s"
        cursor.execute(delete_booking_query, (booking_id,))
        
        # Also remove entries from related tables (BookingFlight, BookingHotel, BookingCar)
        cursor.execute("DELETE FROM BookingFlight WHERE BookingID = %s", (booking_id,))
        cursor.execute("DELETE FROM BookingHotel WHERE BookingID = %s", (booking_id,))
        cursor.execute("DELETE FROM BookingCar WHERE BookingID = %s", (booking_id,))

        db_connection.commit()
        cursor.close()
        return "Booking removed successfully"
    else:
        cursor.close()
        return "Booking not found or does not belong to this user"
