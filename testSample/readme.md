# Sample fastapi code

To read Database from your code, put Database and .env file in CWD of your app or main file, or else you willget pydantic validation error
"https://stackoverflow.com/questions/71949467/pydantic-validation-error-for-basesettings-model-with-local-env-file"

Use the procfile provided and use foreman to start your server.

The db is prepopulated with a classes table and have some 3 rows in it, use end point "http://127.0.0.1:5000/docs" to view the api docs.
Rest code is simple refer main.py file
