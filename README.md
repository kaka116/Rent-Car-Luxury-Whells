# Rent-Car-Luxury-Whells
Project Purpose:
This project is an example of a website for a car rental service,
with an associated database and the possibility of connecting it to an
internal application for data verification, payments,
and direct modification of vehicle information.

Technologies and Dependencies:

Flask: Web development framework.
Bootstrap: CSS framework for responsive design.
SQLite: Database for data storage.
Python 3.10: Required Python version.

Module Installation:
pip install flask
pip install flask-login
pip install flask-sqlalchemy
pip install python-dateutil

Development Environment Setup:
Make sure you have Python 3.10 installed.

How to Run the System:
Run the main.py file to start the web server and website operation.
The system will create the SQLite database if it does not already exist, as well as add vehicles to the database as needed.
The necessary folders will be created automatically when functionalities such as uploading payment receipts are activated.

File Structure:

main.py: Main file for running the server and controlling functionalities.
views/: Contains the general website routes (e.g., page display).
auth/: Routes for user authentication (login, account creation).
__init__/: Application initialization, database configuration, and component integration.
models/: Database table models (SQLAlchemy).
templates/: Contains the HTML pages rendered by Flask.
static/: Contains vehicle images and logos.
instance/: Contains the SQLite database and folders for storing user-uploaded documents (e.g., payment receipts).
