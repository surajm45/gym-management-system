1) create venv (if not already)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

2) install requirements
   pip install -r requirements.txt

3) create database (MySQL Workbench)
   CREATE DATABASE gymdb;

4) set environment (.env) correctly (DB URI + MAIL creds if needed)

5) create tables (development)
   python create_tables.py

6) start server
   python run.py

7) open browser
   http://127.0.0.1:5000/
