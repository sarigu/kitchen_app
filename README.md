# Kitchen App

## ER Diagram

Follows soon

## Explanation of project idea

“Kitchen App” is an organizing tool for shared kitchens. I am living in a dorm, where we share a kitchen with up to 20 people. Many of the kitchens struggle with organizing the shared space over Facebook groups. 
The project is an attempt to provide shared kitchen spaces with tools to solve the problem. The tools are in regards to organizing finances, distributing tasks, organizing events and communication within the group.
Each kitchen can create a room for their kitchen in the app. The room has (multiple) admins and members. Room admins can view a room as a normal member or in admin mode (which comes with additional functionalities).

## Start virtual environment

Start the virtual environment

Navigate to the projects folder

Install packages

`pip install -r requirements.txt`

## Migrate project

`python manage.py makemigrations`

`python manage.py migrate`

## Run project

`python manage.py runserver`

## Login to the kitchen app

Go to: `localhost:8000`

username: admin <br />
password: admin

## Login to admin pannel

Go to: `localhost:8000/admin`

username: admin <br />
password: admin
