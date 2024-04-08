Career Counselling App (Django Version)

The Career Counselling App is built using the Django framework, providing comprehensive support to students in exploring, planning, and achieving their career goals. It offers features such as career exploration, aptitude testing, and college suggestions based on results.
Table of Contents

    Features
    User Characteristics
    Functional Requirements
    Installation
    Usage
    Contributing
    License

Features

    Comprehensive Support: The app assists students in exploring, planning, and achieving their career goals.
    Easy Registration: Simple registration process for both students and colleges.
    Career Exploration: Students can explore various career paths.
    Aptitude Testing: Students can take aptitude exams, and colleges are suggested based on the results.

User Characteristics
Admin

    Login: Access the system using credentials.
    View User Profiles: Access and view user accounts.
    CURD Operations: Perform create, update, read, delete operations on user profiles.

Student

    Registration: Register in the application.
    Login: Access the services using credentials.
    View Colleges: Explore colleges based on aptitude results, location, and courses.
    Edit Profile: Modify user profile information.
    Take Aptitude Test: Participate in aptitude testing.

College

    Registration: Register in the application.
    Login: Access the services using credentials.
    Edit Profile: Update description and courses offered.

Functional Requirements
Admin

    Login: Authenticate with username and password.
    View User Profiles: Access user accounts.
    CURD Operations on User Profiles: Create, update, read, delete user profiles.

Student

    Registration: Sign up for the app.
    Login: Access account.
    View Colleges: Explore available colleges.
    Edit Profile: Modify user details.
    Take Aptitude Test: Participate in aptitude testing.

College

    Registration: Register for the app.
    Login: Access account.
    Edit Profile: Update college information.

Installation

    1)Clone the repository to your local machine:
    git clone <repository_url>

    2)Install dependencies:
    pip install -r requirements.txt

    3)Apply migrations:
    python manage.py migrate

    Usage

    Start the development server:
    python manage.py runserver


    Access the application in your web browser at http://localhost:8000.




    

    
