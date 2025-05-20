# My Flask Web Application

A simple Flask web application demonstrating user authentication, profile management, and basic web application features.

## Features

- **User Registration**: New users can create an account by providing a username, email, and password.
- **User Login/Logout**: Registered users can log in to access protected areas and log out to end their session.
- **Profile Viewing and Editing**: Users can view their own and other users' profiles. Authenticated users can edit their own profile information, including first name, last name, and a short biography.

## Prerequisites

- Python 3.8+

## Setup and Run Instructions

### 1. Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

**On macOS and Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies

With your virtual environment activated, install the required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

The application uses environment variables for configuration. Create a `.flaskenv` file in the project root with the following content (optional, but good practice for development):

```
FLASK_APP=run.py
FLASK_ENV=development # Enables debug mode
# SECRET_KEY=your_actual_secret_key # For production, generate a strong secret key
```

And a `.env` file for sensitive or instance-specific configurations (this file should be in .gitignore for public repos):
```
# SECRET_KEY=your_actual_secret_key # Can also be placed here
# DATABASE_URL=your_production_database_url # For production database
```
If `SECRET_KEY` is not set, a default one will be used for development, but it's crucial to set a strong one for production.

### 4. Set Up the Database

This application uses Flask-Migrate to manage database schemas.

**Initialize the Database (run only once if you haven't already):**
If the `migrations` folder does not exist, initialize it:
```bash
# Ensure FLASK_APP is set in your environment or .flaskenv
# export FLASK_APP=run.py # If not using .flaskenv
flask db init
```
*Note: In this project, `migrations` folder and initial migration might already be present. If so, you can skip `flask db init`.*

**Create Migrations:**
If you've made changes to the models (`app/models.py`) or this is the first time setting up after cloning and `migrations/versions` is empty or you need to capture model changes:
```bash
# flask db migrate -m "Descriptive message for your migration"
flask db migrate -m "initial migration" 
```
*(If an "initial migration" already exists from project setup, and you are setting up an existing project, you might not need to run migrate again unless models have changed since the last migration in the repo.)*

**Apply Migrations to the Database:**
This command applies the migration scripts to create or update your database schema.
```bash
flask db upgrade
```
This will create an `instance/app.db` SQLite database file by default.

### 5. Run the Application

Once the dependencies are installed and the database is set up, you can run the application:

```bash
python run.py
```
or
```bash
flask run
```

The application will typically be available at `http://120.0.0.1:5000/`.

## Running Tests

To run the unit tests for the application:

1. Ensure your virtual environment is activated and all dependencies (including test dependencies if any were separate) are installed.
2. Navigate to the project root directory.
3. Run the following command:

```bash
python -m unittest discover tests
```

This will discover and run all tests located in the `tests` directory. The tests are configured to use an in-memory SQLite database, so they won't affect your development database.

---

This README provides basic instructions. For more advanced deployment or configuration, refer to the Flask documentation and the documentation of its extensions.
