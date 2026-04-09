# 🚀 Flask API Project

---

## 📌 Requirements

* Python 3.12.3
* pip

### 🔍 Check Python Version

```bash
py -V
```

---

## ⚙️ Installation

### 🪟 Windows (Virtual Environment)

```bash
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

### 🐧 Linux (Virtual Environment)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ▶️ Usage

### 🚀 Start API Server

```bash
py app.py
```

---

## 🌐 API Example

```python
@app.route("/create", methods=["POST"])
```

---

## 📦 GitHub Setup & Deployment

### 🔧 Initialize Git

```bash
git init
git add .
git commit -m "Initial commit - Flask app"
```

### 🔗 Add Remote Repository

```bash
git remote add origin https://github.com/your-username/flask-app.git
# Example:
git remote add origin https://github.com/Manjunath3009/flask-app.git
```

---

### ❌ Remove Unwanted Files (like venv)

```bash
git rm -r --cached venv
git commit -m "Removed venv from repository"
git push
```

---



---

### Git push and commit from vscode directly using gitlens

```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"

git config --global user.email manju3009.m@gmail.com
git config --global user.name Manjunath3009

```

---

### 🔄 Update README Changes

```bash
git add README.md
git commit -m "Updated README"
git push
```

---

## 📬 Postman Usage

1. Run the API server:

   ```bash
   py apiserver.py
   ```
2. Copy the generated localhost URL
3. Open Postman
4. Select **POST** method
5. Go to **Body → Raw → JSON**
6. Enter request payload
7. View response in the response panel

---

## ☁️ Deploy to AWS (Using Zappa)

### 🔑 Configure AWS Credentials

1. Login to AWS Console
2. Go to **IAM → Users → Security Credentials**
3. Create:

   * Access Key
   * Secret Key

---

### 📦 Install Required Packages

```bash
pip install zappa
pip install awscli
```

*(Skip if already in requirements.txt)*

---

### ⚙️ Configure AWS CLI

```bash
aws configure
```

#### Example:

```
AWS Access Key ID: YOUR_ACCESS_KEY_ID
AWS Secret Access Key: YOUR_SECRET_ACCESS_KEY
Default region name: ap-south-1
Default output format: json
```

---

### 🚀 Initialize Zappa

```bash
zappa init
```

#### Example Configuration:

```json
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
```

---

### 🚀 Deploy Application

```bash
zappa deploy dev
```

---

### ✅ Successful Deployment

You will receive a URL like:

```
https://vucq89hoec.execute-api.eu-north-1.amazonaws.com/dev
```

---

# 📚 Additional Knowledge

## 🌐 HTTP Methods

### 1. GET

* **Purpose:** Retrieve data
* **Example:**

  * `GET /users`
  * `GET /users/123`
* **Idempotent:** Yes

---

### 2. POST

* **Purpose:** Create new resource
* **Example:**

  * `POST /users`
* **Idempotent:** No

---

### 3. PUT

* **Purpose:** Update/replace resource
* **Example:**

  * `PUT /users/123`
* **Idempotent:** Yes

---

### 4. DELETE

* **Purpose:** Delete resource
* **Example:**

  * `DELETE /users/123`
* **Idempotent:** Yes

---

## 👨‍💻 Author

Manjunath M

---
