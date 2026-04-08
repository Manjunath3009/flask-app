## Requirements
- Python 3.12.3
- pip

## Check python version 
py -V

## Installation on Windows (virtual environment)
```
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Installation on Linux(virtual environment)
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
---
## to start API server
---
py app.py 
---

## API Server Usage
## example 
-@app.route("/create", methods=["POST"])

## GIThub deploy
```
-- Create gitignore file to ignore the mentioned file  to push into github
-- cmd: git init -- to add git the your project dicrectory
-- cmd: git add . -- add the file to git package that are ready to push into github
-- cmd: git commit -m "Initial commit - Flask app"
-- cmd: git remote add origin https://github.com/your-username/flask-app.git
-- ex: git remote add origin https://github.com/Manjunath3009/flask-app.git

-- remove file added from repo
cmd: git rm -r --cached venv
cmd: git commit -m "Removed venv from repository"
cmd: git push

-- push when update readme commands
cmd: git add readme.md
cmd: git commit -m "Updated README"
cmd: git push

```

## POSTMAN Usage
```
-- After running python apiserver.py command , a running localhost http link will be generated, used that link in POSTMAN application as  "POST" method 
-- Go to Body , select type raw and enter your request in json format
-- Your response will be availble in the response window of POSTMAN

```
## Deploy to AWS Cloud 

Login to your AWS Cloud
Go to IAM > Users> Security credentails > create a access key and secret key
'''
pip install zappa     // if provided in requirements.txt , then no need to run this command
pip install awscli    // if provided in requirements.txt , then no need to run this command

'''
aws configure 
'''
example of credentials need to be entered:

AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
Default region name [None]: ap-south-1
Default output format [None]: json

'''
zappa init
'''

enter the requested details as below 

example:
{
    "dev": {
      "aws_region": "us-east-1", 
      "project_name": "api-venv",
      "profile_name": null,
      "exclude": [
            "boto3",
            "dateutil",
            "botocore",
            "s3transfer",
            "concurrent"
        ],
       "manage_roles": false, 
        "role_name": "MyLambdaRole", 
      "s3_bucket": "myapi-bucket",
      "app_function": "apiserver.app",
      "runtime": "python3.11",
      "memory_size": 128,
      "timeout_seconds": 30
    }
  }

'''
zappa deploy dev

'''
## Successful deployment : you will receive a aws generated link 
Deployment complete!: https://vucq89hoec.execute-api.eu-north-1.amazonaws.com/dev



---------------------------- EXTRA--- FOR KNOWLEDGE PURPOSE ONLY-------------------------------------------------------------------------------
## API Method options

In the context of web development, particularly with RESTful APIs, GET, POST, PUT, and DELETE are the four primary HTTP methods used to perform operations on resources. Here's a breakdown of each:

## 1. GET
    Purpose: Retrieve data from the server.
    Usage: When you want to request data or a resource without making any changes to it.
    Example:
    Fetching a list of users: GET /users
    Fetching a specific user by ID: GET /users/123
    Idempotency: Yes (multiple identical requests have the same effect as a single request).

## 2. POST
    Purpose: Send data to the server to create a new resource.
    Usage: When you want to submit data to the server to create a new record/resource.
    Example:
    Creating a new user: POST /users with user data in the request body.
    Idempotency: No (submitting the same data multiple times may result in multiple records).
## 3. PUT
    Purpose: Update an existing resource or create a new resource if it doesn't exist.
    Usage: When you want to completely replace the state of a resource with new data.
    Example:
    Updating a user’s details: PUT /users/123 with updated user data in the request body.
    Idempotency: Yes (sending the same update request multiple times results in the same state).
## 4. DELETE
    Purpose: Remove a resource from the server.
    Usage: When you want to delete a specific resource.
    Example:
    Deleting a user by ID: DELETE /users/123
    Idempotency: Yes (deleting the same resource multiple times has the same effect as deleting it once).