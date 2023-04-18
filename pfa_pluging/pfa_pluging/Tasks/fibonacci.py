from girder_worker.app import app

@app.task
def fibonacci(n, filename, user_fullname, user_email):
    if n == 1 or n == 2:
        return 1
    return fibonacci(n-1, filename, user_fullname, user_email) + fibonacci(n-2, filename, user_fullname, user_email)