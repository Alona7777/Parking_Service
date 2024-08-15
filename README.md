# Final_project






### Get started

1) Clone repository:

    ```https://github.com/Alona7777/Final_project```


2) To create a VENV virtual environment, you need to execute the following commands in the terminal:

    - 1. ```python3 -m venv venv```
    - 2. ```source venv/bin/activate```
    - 3. ```pip install -r requirements.txt```

3) Using the ```example.env``` make your own  ```.env ```

4) Go to the ```parking_system``` directory:  
    ```cd``` your path to this directory

5) Run docker compose:

    ```docker compose up -d```

6) Run migration:
    ```python manage.py makemigrations```
    ```python manage.py migrate```


