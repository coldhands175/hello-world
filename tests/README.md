# Running Tests

To run the unit tests for this Flask application, ensure you have the necessary dependencies installed (Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF, etc.).

Navigate to the root directory of the project (the one containing the `app` and `tests` directories).

You can discover and run all tests using the following command:

```bash
python -m unittest discover tests
```

Alternatively, you can run specific test files:

```bash
python -m unittest tests.test_auth
python -m unittest tests.test_profile
```

## Test Configuration

The tests are configured to use an in-memory SQLite database and will not affect your development database. The configuration `TestConfig` in `config.py` is used for this purpose, which includes `TESTING = True`, `SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'`, and `WTF_CSRF_ENABLED = False`. The application factory `create_app` in `app/__init__.py` automatically selects this configuration when the tests are run (specifically, the test cases instantiate the app with `TestConfig`).
