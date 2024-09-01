# Travel Booking System

This repository contains the implementation of a Travel Booking System using Python, MySQL, and Streamlit. The project is divided into multiple components, each serving a specific purpose in the overall system.

## Repository Contents

- **Tasks_travel_booking.ipynb**: This Jupyter Notebook demonstrates the various tasks performed as part of the travel booking system. It includes tasks such as table creation, data insertion, normalization, and indexing in MySQL using Python.
  
- **booking_functions.py**: This Python script contains the functions used to create buttons and manage functionalities within the Streamlit web application.

- **app.py**: The main Streamlit app script. This file contains the code to run the web interface for the Travel Booking System.

- **environment.yml**: A YAML file listing all the dependencies required to run the scripts in this repository. Make sure to install these dependencies in a conda environment before running any code.

## Setup Instructions

1. **Create the MySQL Database:**
   - Before running the scripts, you need to create a database named `travel_booking` in your MySQL CLI. Use the following command:
     ```bash
     mysql -u root -p -e "CREATE DATABASE travel_booking;"
     ```

2. **Set Up Environment Variables:**
   - To ensure a secure connection to the MySQL database, the following environment variables should be set up on your system:
     ```bash
     export MYSQL_USER='your_mysql_username'
     export MYSQL_PASSWORD='your_mysql_password'
     export MYSQL_HOST='your_mysql_host'  # e.g., localhost
     export MYSQL_DATABASE='travel_booking'
     ```
   - These variables can be set in your terminal session or added to your shell profile (e.g., `~/.bashrc`, `~/.zshrc`) for persistence across sessions. This setup ensures that sensitive information is not hardcoded in the source code.

   Here's how the environment variables are used in the Python scripts:

   ```python
   import os
   import mysql.connector

   user = os.getenv("MYSQL_USER")
   password = os.getenv("MYSQL_PASSWORD")
   host = os.getenv("MYSQL_HOST")
   database = os.getenv("MYSQL_DATABASE")

   db_connection = mysql.connector.connect(
       host=host,
       user=user,
       password=password,
       database=database
   )

   cursor = db_connection.cursor()
3. **Run the Jupyter Notebook:**
   - Open and run `Tasks_travel_booking.ipynb` to see the implementation of various database tasks and operations.

4. **Run the Streamlit App:**
   - Start the Streamlit web application by running the following command:
     ```bash
     streamlit run app.py
     ```
   - This will launch the web interface in your default web browser.

## Usage

- The **Jupyter Notebook** (`Tasks_travel_booking.ipynb`) is mainly for demonstration and testing of SQL operations, including table creation, data insertion, and normalization.
  
- The **Streamlit App** (`app.py`) provides a user-friendly web interface for interacting with the travel booking system. The functionalities include searching for bookings, managing user profiles, and processing payments.

- The **booking_functions.py** script provides modular functions that are called within the Streamlit app to handle various backend operations.

## Notes

- Ensure the `travel_booking` database is properly set up and environment variables are correctly configured before running the app.
- The code is designed to be secure by keeping sensitive information like the database user, password, and host outside of the source code and instead using environment variables.

---
