# Back-End-Development-Songs

A Flask-based microservice designed to manage a catalog of songs using a MongoDB backend instance. This repository contains the complete implementation of a RESTful CRUD API, including service health analytics, full data synchronization, single resource filtering, modifications, and deletions.

## 🛠️ Tech Stack & Dependencies
* **Framework:** Python / Flask
* **Database Driver:** PyMongo (MongoDB Client)
* **Configuration & Environment:** Python-dotenv / OS Environment

---

## 🚀 Getting Started

### 1. Environment Variables
The application dynamically connects to a MongoDB database utilizing the following environment metrics:
* `MONGODB_SERVICE`: The target host IP/address of your running database service instance.
* `MONGODB_USERNAME`: Database administrative username (`root`).
* `MONGODB_PASSWORD`: Secure connection credential phrase.

### 2. Launching the Application
Execute the localized deployment server environment with the following initialization configuration sequence:
```bash
MONGODB_SERVICE=<YOUR_MONGO_IP> MONGODB_USERNAME=root MONGODB_PASSWORD=<YOUR_PASSWORD> FLASK_APP=app.py flask run --debugger --reload