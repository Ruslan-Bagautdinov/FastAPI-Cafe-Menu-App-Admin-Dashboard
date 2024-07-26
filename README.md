# FastAPI Cafe Menu App Admin Dashboard

FastAPI Admin Dashboard is a backend service for a React app, providing an admin dashboard for the cafe app. It allows users to login as a superuser (admin) or a cafe owner (user). Users can manage their cafe profiles, dishes, and passwords. Superusers can manage all cafes and users.

## Features

- **Authentication**: Login as a superuser or user.
- **User Management**: View, add, and edit user profiles.
- **Restaurant Management**: View, add, and edit cafe profiles.
- **Dish Management**: View, add, and edit dishes for cafes.
- **Password Management**: Change or reset passwords.
- **Email Operations**: Retrieve emails for password resets.
- **Image Operations**: Manage images related to cafes and dishes.

## Setup

### Prerequisites

- Python 3.7+
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/fastapi-admin-dashboard.git
   cd fastapi-admin-dashboard
   ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up your environment variables by creating a .env file in the root directory with the following content:

```dotenv
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
SMTP_SERVER=your_smtp_server
SMTP_PORT=your_smtp_port
SENDER_EMAIL=your_sender_email
SENDER_PASSWORD=your_sender_password
HOME_DB=False
HOME_EMAIL=False
WORK_DATABASE_URL=your_work_database_url
LOCAL_DATABASE_URL=your_local_database_url
LOCAL_SMTP_SERVER=your_local_smtp_server
LOCAL_SMTP_PORT=your_local_smtp_port
LOCAL_SENDER_EMAIL=your_local_sender_email
LOCAL_SENDER_PASSWORD=your_local_sender_password
WORK_SMTP_SERVER=your_work_smtp_server
WORK_SMTP_PORT=your_work_smtp_port
WORK_SENDER_EMAIL=your_work_sender_email
WORK_SENDER_PASSWORD=your_work_sender_password
LOCAL_SERVER_HOST=your_local_server_host
LOCAL_SERVER_PORT=your_local_server_port
WORK_SERVER_HOST=your_work_server_host
WORK_SERVER_PORT=your_work_server_port
PW_OK_PAGE=your_pw_ok_page
```

5. Run the application:

   ```sh
   uvicorn main:app --reload
   ```

## API Endpoints

### Authentication

- POST /api/auth/login: Authenticates a user and returns an access token.

- POST /api/auth/register: Registers a new user with restaurant details and returns registration details.

### User Management

- GET /api/users/get_all_users: Retrieve all users. (Only for superusers)

- GET /api/users/get_all_superusers: Retrieve all superusers for superusers. (Only for superusers)

- POST /api/users/approve_user: Approve a user by email. (Only for superusers)

- POST /api/users/create_new_user: Create a new user with specified role and restaurant details. (Only for superusers)

- DELETE /api/users/delete_user_by_email/: Delete a user by email. (Only for superusers)

### Restaurant Management

- GET /api/restaurants/get_all_restaurants: Retrieve all restaurants for superusers.

- GET /api/restaurants/get_restaurant: Retrieve a user profile by email.

- PATCH /api/restaurants/update_restaurant: Update a user profile by email.

### Dish Management

- GET /api/dishes/all_categories/: Retrieve a dictionary mapping category IDs to their names.

- POST /api/dishes/categories_in_restaurant/: Retrieve categories used in a restaurant linked with the user's email.

- POST /api/dishes/dish_by_id/: Retrieve a dish by its ID.

- POST /api/dishes/create/: Create a new dish.

- PATCH /api/dishes/update/: Update an existing dish.

- DELETE /api/dishes/delete/: Delete a dish by its ID.

- POST /api/dishes/dishes_by_email/: Retrieve dishes by user email. If a category is provided, only dishes from that category are returned.

### Password and Email Operations

- POST /api/emails/send-email/: Send an email to a specified recipient.

- POST /api/emails/request-reset/: Request a password reset for a user.

- GET /api/emails/reset-password/: Reset a user's password using a valid token.

- POST /api/emails/change_password: Change user password.

### Image Operations

- GET /api/images/: Retrieves a photo from the static photo folder or returns a default photo if the specified photo is not found.

- POST /api/images/upload/: Upload a file to the server.

### Contributing
Contributions are welcome! Please open an issue or submit a pull request.

### License
This project is free for use. No license is required
