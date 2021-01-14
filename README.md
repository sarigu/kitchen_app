# Kitchen App

## Explanation of project idea

“Kitchen App” is an organizing tool for shared kitchens. I am living in a dorm, where we share a kitchen with up to 20 people. Many of the kitchens struggle with organizing the shared space over Facebook groups. 
The project is an attempt to provide shared kitchen spaces with tools to solve the problem. The tools are in regards to organizing finances, distributing tasks, organizing events and communication within the group.
Each kitchen can create a room for their kitchen in the app. The room has (multiple) admins and members. Room admins can view a room as a normal member or in admin mode (which comes with additional functionalities).

## Start virtual environment
Start your virtual environment 

## Install packages

Navigate to the projects folder

Install packages in project root:

`pip install -r requirements.txt`

## Migrate project

`python manage.py makemigrations`

`python manage.py migrate`

## Redis Server

Install Docker

Run Redis Server:

`docker run -p 6379:6379 redis`

## Run the Django RQ Worker

Open another terminal window

`python manage.py rqworker`

Note: the virtual environment needs to be active

## Run project

Open another terminal window (active venv)

`python manage.py runserver`

## Login to the kitchen app

Go to: `localhost:8000`

username: admin <br />
password: admin

Rooms: <br />
user is a room admin: Django  <br />
user is a room member: Toast is awesome

## Login to admin panel

Go to: `localhost:8000/admin`

username: admin <br />
password: admin
