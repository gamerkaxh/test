# Flask API Tutorial

A simple Flask application to teach REST API concepts interactively. It includes multiple endpoints with dummy data and a built-in UI to test API calls directly from the browser.

## What You'll Learn

- **REST API fundamentals** - GET, POST, PUT, DELETE, PATCH methods
- **HTTP status codes** - 200, 201, 400, 404, 500
- **Query parameters** - Filtering data with URL parameters
- **JSON request/response** - How APIs communicate data
- **CRUD operations** - Create, Read, Update, Delete

## Project Structure

```
flask-api-tutorial/
├── app.py                  # Main Flask application with all API endpoints
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── templates/
│   └── index.html          # Frontend UI
└── static/
    ├── style.css           # Styling
    └── script.js           # Frontend JavaScript for API calls
```

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
python app.py
```

### 3. Open in Browser

Visit [http://localhost:5000](http://localhost:5000) to see the interactive UI.

## API Endpoints

### API Info
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api` | List all available endpoints |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | Get all users (filter: `?role=admin`) |
| GET | `/api/users/<id>` | Get a specific user |
| POST | `/api/users` | Create a new user |
| PUT | `/api/users/<id>` | Update a user |
| DELETE | `/api/users/<id>` | Delete a user |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | Get all products (filter: `?category=`, `?in_stock=`) |
| GET | `/api/products/<id>` | Get a specific product |
| POST | `/api/products` | Create a new product |
| PUT | `/api/products/<id>` | Update a product |
| DELETE | `/api/products/<id>` | Delete a product |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Get all tasks (filter: `?completed=`, `?priority=`) |
| GET | `/api/tasks/<id>` | Get a specific task |
| POST | `/api/tasks` | Create a new task |
| PUT | `/api/tasks/<id>` | Update a task |
| DELETE | `/api/tasks/<id>` | Delete a task |
| PATCH | `/api/tasks/<id>/toggle` | Toggle task completion |

### Search & Stats
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search?q=<query>` | Search across all data |
| GET | `/api/stats` | Get aggregated statistics |

## Example API Calls (using curl)

```bash
# Get all users
curl http://localhost:5000/api/users

# Get users filtered by role
curl http://localhost:5000/api/users?role=admin

# Create a new user
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "role": "user"}'

# Update a user
curl -X PUT http://localhost:5000/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice Updated"}'

# Delete a user
curl -X DELETE http://localhost:5000/api/users/1

# Search across all data
curl http://localhost:5000/api/search?q=laptop

# Get statistics
curl http://localhost:5000/api/stats
```

## Notes

- Data is stored **in-memory** and resets when the server restarts.
- This is for **learning purposes** only — not intended for production use.
- The UI makes real API calls so you can see requests and responses in action.
