# Community Helper Hub

A full-stack web application that connects users with trusted local helpers in their neighborhood.

## 🔧 Tech Stack

- **Frontend**: HTML, CSS, JavaScript (high-graphic, responsive, interactive)
- **Backend**: Python Flask (REST APIs, server-side logic)
- **Database**: SQLite (store users, helpers, service requests, feedback)
- **Authentication**: Firebase Google Auth + email/password option

## 🎯 Core Modules

### User Module

- Register/login with email/password and Google Auth
- Post service requests with categories, descriptions, and deadlines
- Manage personal dashboard of active and past requests

### Helper Module

- Create a profile with skills, experience, and availability
- Respond to service requests directly
- Manage bookings with status updates

### Admin Module

- Verify helpers and users
- Manage reported complaints
- Oversee all service requests, user activity, and data

### Feedback Module

- Users leave star ratings and text reviews for helpers
- Complaints system with tracking and resolution workflow

## ⚙️ Workflow Enhancements

- **Service Posting Flow**: Step-by-step guided form
- **Helper Booking Flow**: Interactive booking calendar with confirmation popup
- **Admin Flow**: Dashboard with helper verification status and request approvals
- **Feedback Flow**: Animated star rating system + expandable complaint details

## 🎨 UI & Design

- High-graphic and interactive design with smooth animations
- Dual Theme (Dark & Light) with theme switcher toggle
- Modern typography (Poppins/Inter)
- Responsive layouts for all devices

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git

### Installation

1. Clone the repository

   ```
   git clone <repository-url>
   cd Community-Application
   ```

2. Create and activate a virtual environment

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies

   ```
   pip install -r requirements.txt
   ```

4. Set up Firebase configuration
   - Create a Firebase project
   - Enable Authentication (Email/Password and Google)
   - Create a `firebase_config.json` file with your Firebase credentials

5. Initialize the database

   ```
   python models/database.py
   ```

6. Run the application

   ```
   python app.py
   ```

7. Access the application at http://localhost:5000

## 📂 Project Structure

These are the core files and directories that define the application:

- **`app/`**: Contains all application logic, including models, controllers, templates, and static files.
- **`config/`**: Holds configuration files (excluding private keys/secrets).
- **`run.py`**: The main entry point to start the Flask application.
- **`requirements.txt`**: Lists all Python libraries and dependencies.
- **`.env.example`**: A template for environment variables (without actual secrets).
- **`.gitignore`**: Specifies files and folders that should not be tracked by Git.
- **`README.md`**: Project documentation and setup instructions.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
