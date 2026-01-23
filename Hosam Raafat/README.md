# Notes Web App

Simple notes web application built with Flask and MariaDB, deployed on AWS EC2 (RHEL 10).

Features:
- User login and register
- Create, edit, delete notes
- Show last update time for each note
- Save notes edit history
- MariaDB database
- Database backup on /backup disk

Tech:
- Python (Flask)
- MariaDB
- HTML & CSS
- AWS EC2

Run:
pip3 install flask mysql-connector-python
python3 app.py

Backup:
mysqldump -u root -p notes_app > /backup/notes_app_backup.sql

Author:
Hosam Raafat