import streamlit as st
import pandas as pd
from datetime import datetime 
from booking_functions import (
    connect_to_db, verify_user_login, is_admin, make_booking, view_available_flights, 
    view_available_hotels, view_available_cars, filter_flights, 
    get_user_bookings, add_travel_option, view_user_bookings, view_all_users,view_all_flights,
    view_all_hotels,view_all_cars,create_user_account,remove_booking
)

# Initialize session state variables for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.is_admin = False

# Title for the app
st.title("Travel Booking System")

# Login form should be at the beginning
if not st.session_state.logged_in:
    st.header("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        db_connection = connect_to_db()
        
        # Check if the user is admin
        if is_admin(email, password):
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.success("Logged in as Admin")
        
        # Check if the user is a registered user
        else:
            user_id = verify_user_login(db_connection, email, password)
            if user_id:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.success("Logged in as User")
            else:
                st.error("Invalid email or password")

        db_connection.close()
    st.write("Don't have an account? Sign up below!")

    # Create Account Section
    st.header("Create Account")
    new_name = st.text_input("Name", key="signup_name")
    new_email = st.text_input("Email (for login)", key="signup_email")
    new_password = st.text_input("Password", type="password", key="signup_password")
    new_contact = st.text_input("Contact Number", key="signup_contact")
    
    if st.button("Create Account"):
        db_connection = connect_to_db()
        creation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Automatically set creation time
        create_result = create_user_account(db_connection, new_name, new_email, new_password, new_contact, creation_time)
        db_connection.close()
        st.success(create_result)

# After login: Separate User and Admin Features
if st.session_state.logged_in:
    db_connection = connect_to_db()  # Ensure a fresh connection for logged-in users

    if st.session_state.is_admin:
        st.header("Admin Dashboard")

        # Admin functionalities
        st.subheader("Manage Travel Options")

        # Add a new travel option
        option_type = st.selectbox("Select Type", ["flight", "hotel", "car"])
        if option_type == "flight":
            flight_number = st.text_input("Flight Number")
            departure_city = st.text_input("Departure City")
            arrival_city = st.text_input("Arrival City")
            departure_date = st.date_input("Departure Date")
            arrival_date = st.date_input("Arrival Date")
            price = st.number_input("Price", min_value=0.0)
            availability = st.number_input("Availability", min_value=0, step=1)
            if st.button("Add Flight"):
                details = (flight_number, departure_city, arrival_city, departure_date, arrival_date, price, availability)
                result = add_travel_option(db_connection, "flight", details)
                st.success(result)
        
        elif option_type == "hotel":
            hotel_name = st.text_input("Hotel Name")
            city = st.text_input("City")
            check_in_date = st.date_input("Check-In Date")
            check_out_date = st.date_input("Check-Out Date")
            price_per_night = st.number_input("Price per Night", min_value=0.0)
            availability = st.number_input("Availability", min_value=0, step=1)
            if st.button("Add Hotel"):
                details = (hotel_name, city, check_in_date, check_out_date, price_per_night, availability)
                result = add_travel_option(db_connection, "hotel", details)
                st.success(result)
        
        elif option_type == "car":
            car_model = st.text_input("Car Model")
            city = st.text_input("City")
            rental_date = st.date_input("Rental Date")
            price_per_day = st.number_input("Price per Day", min_value=0.0)
            availability = st.number_input("Availability", min_value=0, step=1)
            if st.button("Add Car"):
                details = (car_model, city, rental_date, price_per_day, availability)
                result = add_travel_option(db_connection, "car", details)
                st.success(result)

        st.subheader("View Users")
        if st.button("Show All Users"):
            users = view_all_users(db_connection)
            if users:
            # Convert the users list into a pandas DataFrame
                df_users = pd.DataFrame(users, columns=["UserID", "Name", "Email", "ContactNumber"])
            # Display the DataFrame in Streamlit as a table
                st.dataframe(df_users)
        else:
            st.write("No users found.")


        st.subheader("View All Bookings")
        if st.button("Show All Bookings"):
            bookings = view_user_bookings(db_connection)
            if bookings:
        # Convert the bookings list into a pandas DataFrame
                df_bookings = pd.DataFrame(bookings, columns=["BookingID", "UserName", "BookingDate", "TotalAmount", "CreationTime"])
        
        # Handle datetime and decimal formatting if necessary
                df_bookings['BookingDate'] = pd.to_datetime(df_bookings['BookingDate'])
                df_bookings['TotalAmount'] = df_bookings['TotalAmount'].astype(float)
        
        # Attempt to convert CreationTime, handling any exceptions
                try:
                    df_bookings['CreationTime'] = pd.to_datetime(df_bookings['CreationTime'])
                except Exception as e:
                    st.write(f"Error converting CreationTime: {e}")
                    st.write("Displaying CreationTime as it is.")

        # Display the DataFrame in Streamlit as a table
                st.dataframe(df_bookings)
            else:
                st.write("No bookings found.")
   

        st.subheader("View Travel Options")

        # View Flights Table
        if st.button("View All Flights"):
            flights = view_all_flights(db_connection)
            if flights:
                df_flights = pd.DataFrame(flights, columns=["FlightID", "FlightNumber", "DepartureCity", "ArrivalCity", "DepartureDate", "ArrivalDate", "Price", "Availability"])
                st.dataframe(df_flights)
            else:
                st.write("No flights found.")

        # View Hotels Table
        if st.button("View All Hotels"):
            hotels = view_all_hotels(db_connection)
            if hotels:
                df_hotels = pd.DataFrame(hotels, columns=["HotelID", "Name", "City",  "PricePerNight","RoomType", "Availability"])
                st.dataframe(df_hotels)
            else:
                st.write("No hotels found.")

        # View Cars Table
        if st.button("View All Cars"):
            cars = view_all_cars(db_connection)
            if cars:
                df_cars = pd.DataFrame(cars, columns=["CarID", "Model", "City", "RentalDate", "PricePerDay", "Availability"])
                st.dataframe(df_cars)
            else:
                st.write("No cars found.")
        st.subheader("Generate Reports")

        # Report: Summary of Bookings by Travel Option
        if st.button("Summary of Bookings by Travel Option"):
            summary_query = """
            SELECT 'Flight' AS Type, FlightID AS OptionID, COUNT(*) AS BookingCount, SUM(Booking.TotalAmount) AS TotalRevenue
            FROM BookingFlight
            JOIN Booking ON BookingFlight.BookingID = Booking.BookingID
            GROUP BY FlightID
            UNION ALL
            SELECT 'Hotel' AS Type, HotelID AS OptionID, COUNT(*) AS BookingCount, SUM(Booking.TotalAmount) AS TotalRevenue
            FROM BookingHotel
            JOIN Booking ON BookingHotel.BookingID = Booking.BookingID
            GROUP BY HotelID
            UNION ALL
            SELECT 'Car' AS Type, CarID AS OptionID, COUNT(*) AS BookingCount, SUM(Booking.TotalAmount) AS TotalRevenue
            FROM BookingCar
            JOIN Booking ON BookingCar.BookingID = Booking.BookingID
            GROUP BY CarID
            """
            cursor = db_connection.cursor()
            cursor.execute(summary_query)
            report = cursor.fetchall()
            cursor.close()
    
            if report:
                df_report = pd.DataFrame(report, columns=["Type", "OptionID", "BookingCount", "TotalRevenue"])
                st.dataframe(df_report)
            else:
                st.write("No data available for this report.")
    else:
        st.header("User Dashboard")

        # View user bookings
        st.subheader("Your Bookings")
        if st.button("View Bookings"):
            bookings = get_user_bookings(db_connection, st.session_state.user_id)
    
            if bookings:
                # Convert the bookings list into a pandas DataFrame
                df_bookings = pd.DataFrame(bookings, columns=["BookingID", "BookingDate", "TotalAmount", "FlightID", "HotelID", "CarID"])
        
                # Handle datetime and decimal formatting if necessary
                df_bookings['BookingDate'] = pd.to_datetime(df_bookings['BookingDate'])
                df_bookings['TotalAmount'] = df_bookings['TotalAmount'].astype(float)
        
        # Replace None or NaN with a more readable message
                df_bookings.fillna('None found', inplace=True)
        
        # Display the DataFrame in Streamlit as a table
                st.dataframe(df_bookings)
            else:
                st.write("No bookings found.")
         # Remove a booking
        st.subheader("Remove a Booking")
        booking_id_to_remove = st.number_input("Enter Booking ID to remove", min_value=1, step=1)

        if st.button("Remove Booking"):
            result = remove_booking(db_connection, booking_id_to_remove, st.session_state.user_id)
            if "successfully" in result:
                st.success(result)
            else:
                st.error(result)        
                # View available flights
        st.subheader("View Available Flights")
        departure_city = st.text_input("Departure City")
        arrival_city = st.text_input("Arrival City")
        departure_date = st.date_input("Departure Date")

        if st.button("Search Flights"):
            flights = view_available_flights(db_connection, departure_city, arrival_city, departure_date)
    
            if flights:
                # Convert the flights list into a pandas DataFrame
                df_flights = pd.DataFrame(flights, columns=["FlightID", "FlightNumber", "DepartureCity", "ArrivalCity", "DepartureDate", "ArrivalDate", "Price", "Availability"])
        
        # Handle datetime and decimal formatting if necessary
                df_flights['DepartureDate'] = pd.to_datetime(df_flights['DepartureDate'])
                df_flights['ArrivalDate'] = pd.to_datetime(df_flights['ArrivalDate'])
                df_flights['Price'] = df_flights['Price'].astype(float)
        
                # Display the DataFrame in Streamlit as a table
                st.dataframe(df_flights)
            else:
                st.write("No flights found.")
                # Filter flights
        st.subheader("Filter Flights")
        flight_date_range = st.date_input("Select Date Range for Flights", [])
        if st.button("Filter Flights"):
            flights_filtered = filter_flights(db_connection, departure_city, arrival_city, flight_date_range)
    
            if flights_filtered:
                # Convert the filtered flights list into a pandas DataFrame
                df_filtered_flights = pd.DataFrame(flights_filtered, columns=["FlightID", "FlightNumber", "DepartureCity", "ArrivalCity", "DepartureDate", "ArrivalDate", "Price", "Availability"])
        
        # Handle datetime and decimal formatting if necessary
                df_filtered_flights['DepartureDate'] = pd.to_datetime(df_filtered_flights['DepartureDate'])
                df_filtered_flights['ArrivalDate'] = pd.to_datetime(df_filtered_flights['ArrivalDate'])
                df_filtered_flights['Price'] = df_filtered_flights['Price'].astype(float)
        
        # Display the DataFrame in Streamlit as a table
                st.dataframe(df_filtered_flights)
            else:
                st.write("No flights found for the selected date range.")

        # Make a booking
        st.subheader("Make a Booking")
        booking_date = st.date_input("Booking Date")
        total_amount = st.number_input("Total Amount", min_value=0.0, format="%.2f")
        flight_id = st.number_input("Flight ID", min_value=0, step=1)
        hotel_id = st.number_input("Hotel ID", min_value=0, step=1)
        car_id = st.number_input("Car ID", min_value=0, step=1)
        if st.button("Book Now"):
            result = make_booking(db_connection, st.session_state.user_id, booking_date, total_amount, flight_id, hotel_id, car_id)
            st.success(result)

        # View available hotels and cars
        st.subheader("View Available Hotels and Cars")
        city = st.text_input("City")
        if st.button("Search Hotels"):
            hotels = view_available_hotels(db_connection, city,booking_date)
    
            if hotels:
                # Convert the hotels list into a pandas DataFrame
                df_hotels = pd.DataFrame(hotels, columns=["HotelID", "Name", "City", "PricePerNight", "RoomType", "Availability"])
        
                # Handle decimal formatting if necessary
                df_hotels['PricePerNight'] = df_hotels['PricePerNight'].astype(float)
        
                # Display the DataFrame in Streamlit as a table
                st.dataframe(df_hotels)
            else:
                st.write("No hotels found in the selected city.")
        if st.button("Search Cars"):
            cars = view_available_cars(db_connection, city,booking_date)
    
            if cars:
                # Convert the cars list into a pandas DataFrame
                df_cars = pd.DataFrame(cars, columns=["CarID", "Model", "City", "PricePerDay", "CarType", "Availability"])
        
                # Handle decimal formatting if necessary
                df_cars['PricePerDay'] = df_cars['PricePerDay'].astype(float)
        
                # Display the DataFrame in Streamlit as a table
                st.dataframe(df_cars)
            else:
                st.write("No cars found in the selected city.")

    db_connection.close()  # Close the connection after operations
