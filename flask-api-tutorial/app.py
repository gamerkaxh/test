"""
Flask API Tutorial App
======================
A simple Flask application to teach API concepts.
Demonstrates: GET, POST, PUT, DELETE endpoints with dummy data.
"""

from flask import Flask, jsonify, request, render_template, abort

app = Flask(__name__)

# ============================================================
# DUMMY DATA - In-memory storage (resets on server restart)
# ============================================================

# Users data
users = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "admin"},
    {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "user"},
    {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com", "role": "user"},
    {"id": 4, "name": "Diana Prince", "email": "diana@example.com", "role": "moderator"},
    {"id": 5, "name": "Eve Williams", "email": "eve@example.com", "role": "user"},
]

# Products data
products = [
    {"id": 1, "name": "Laptop", "price": 999.99, "category": "electronics", "in_stock": True},
    {"id": 2, "name": "Headphones", "price": 49.99, "category": "electronics", "in_stock": True},
    {"id": 3, "name": "Coffee Mug", "price": 12.99, "category": "kitchen", "in_stock": False},
    {"id": 4, "name": "Notebook", "price": 5.99, "category": "stationery", "in_stock": True},
    {"id": 5, "name": "Backpack", "price": 79.99, "category": "accessories", "in_stock": True},
    {"id": 6, "name": "Water Bottle", "price": 24.99, "category": "kitchen", "in_stock": True},
]

# Tasks/Todos data
tasks = [
    {"id": 1, "title": "Learn Flask basics", "completed": True, "priority": "high"},
    {"id": 2, "title": "Build REST API", "completed": False, "priority": "high"},
    {"id": 3, "title": "Add authentication", "completed": False, "priority": "medium"},
    {"id": 4, "title": "Write documentation", "completed": False, "priority": "low"},
    {"id": 5, "title": "Deploy to cloud", "completed": False, "priority": "medium"},
]

# Helper to get next ID
def get_next_id(data_list):
    return max(item["id"] for item in data_list) + 1 if data_list else 1


# ============================================================
# UI ROUTE - Serves the frontend
# ============================================================

@app.route("/")
def index():
    """Serve the main UI page."""
    return render_template("index.html")


# ============================================================
# API INFO ENDPOINT
# ============================================================

@app.route("/api", methods=["GET"])
def api_info():
    """Return information about all available API endpoints."""
    return jsonify({
        "message": "Welcome to the Flask API Tutorial!",
        "version": "1.0.0",
        "endpoints": {
            "users": {
                "GET /api/users": "Get all users",
                "GET /api/users/<id>": "Get a specific user",
                "POST /api/users": "Create a new user",
                "PUT /api/users/<id>": "Update a user",
                "DELETE /api/users/<id>": "Delete a user",
            },
            "products": {
                "GET /api/products": "Get all products",
                "GET /api/products/<id>": "Get a specific product",
                "POST /api/products": "Create a new product",
                "PUT /api/products/<id>": "Update a product",
                "DELETE /api/products/<id>": "Delete a product",
            },
            "tasks": {
                "GET /api/tasks": "Get all tasks",
                "GET /api/tasks/<id>": "Get a specific task",
                "POST /api/tasks": "Create a new task",
                "PUT /api/tasks/<id>": "Update a task",
                "DELETE /api/tasks/<id>": "Delete a task",
                "PATCH /api/tasks/<id>/toggle": "Toggle task completion",
            },
            "search": {
                "GET /api/search?q=<query>": "Search across all data",
            },
            "stats": {
                "GET /api/stats": "Get statistics about all data",
            }
        }
    })


# ============================================================
# USERS ENDPOINTS
# ============================================================

@app.route("/api/users", methods=["GET"])
def get_users():
    """Get all users. Supports ?role= filter."""
    role = request.args.get("role")
    if role:
        filtered = [u for u in users if u["role"] == role]
        return jsonify({"users": filtered, "count": len(filtered)})
    return jsonify({"users": users, "count": len(users)})


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get a specific user by ID."""
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route("/api/users", methods=["POST"])
def create_user():
    """Create a new user. Requires: name, email. Optional: role."""
    data = request.get_json()
    if not data or not data.get("name") or not data.get("email"):
        return jsonify({"error": "Name and email are required"}), 400

    new_user = {
        "id": get_next_id(users),
        "name": data["name"],
        "email": data["email"],
        "role": data.get("role", "user")
    }
    users.append(new_user)
    return jsonify({"message": "User created successfully", "user": new_user}), 201


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """Update an existing user."""
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if data.get("name"):
        user["name"] = data["name"]
    if data.get("email"):
        user["email"] = data["email"]
    if data.get("role"):
        user["role"] = data["role"]

    return jsonify({"message": "User updated successfully", "user": user})


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete a user by ID."""
    global users
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    users = [u for u in users if u["id"] != user_id]
    return jsonify({"message": f"User '{user['name']}' deleted successfully"})


# ============================================================
# PRODUCTS ENDPOINTS
# ============================================================

@app.route("/api/products", methods=["GET"])
def get_products():
    """Get all products. Supports ?category= and ?in_stock= filters."""
    result = products.copy()

    category = request.args.get("category")
    if category:
        result = [p for p in result if p["category"] == category]

    in_stock = request.args.get("in_stock")
    if in_stock is not None:
        stock_filter = in_stock.lower() == "true"
        result = [p for p in result if p["in_stock"] == stock_filter]

    return jsonify({"products": result, "count": len(result)})


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Get a specific product by ID."""
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)


@app.route("/api/products", methods=["POST"])
def create_product():
    """Create a new product. Requires: name, price, category."""
    data = request.get_json()
    if not data or not data.get("name") or not data.get("price") or not data.get("category"):
        return jsonify({"error": "Name, price, and category are required"}), 400

    new_product = {
        "id": get_next_id(products),
        "name": data["name"],
        "price": float(data["price"]),
        "category": data["category"],
        "in_stock": data.get("in_stock", True)
    }
    products.append(new_product)
    return jsonify({"message": "Product created successfully", "product": new_product}), 201


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """Update an existing product."""
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    if data.get("name"):
        product["name"] = data["name"]
    if data.get("price") is not None:
        product["price"] = float(data["price"])
    if data.get("category"):
        product["category"] = data["category"]
    if "in_stock" in data:
        product["in_stock"] = bool(data["in_stock"])

    return jsonify({"message": "Product updated successfully", "product": product})


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Delete a product by ID."""
    global products
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    products = [p for p in products if p["id"] != product_id]
    return jsonify({"message": f"Product '{product['name']}' deleted successfully"})


# ============================================================
# TASKS ENDPOINTS
# ============================================================

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Get all tasks. Supports ?completed= and ?priority= filters."""
    result = tasks.copy()

    completed = request.args.get("completed")
    if completed is not None:
        completed_filter = completed.lower() == "true"
        result = [t for t in result if t["completed"] == completed_filter]

    priority = request.args.get("priority")
    if priority:
        result = [t for t in result if t["priority"] == priority]

    return jsonify({"tasks": result, "count": len(result)})


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Get a specific task by ID."""
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)


@app.route("/api/tasks", methods=["POST"])
def create_task():
    """Create a new task. Requires: title. Optional: priority."""
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    new_task = {
        "id": get_next_id(tasks),
        "title": data["title"],
        "completed": False,
        "priority": data.get("priority", "medium")
    }
    tasks.append(new_task)
    return jsonify({"message": "Task created successfully", "task": new_task}), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update an existing task."""
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if data.get("title"):
        task["title"] = data["title"]
    if "completed" in data:
        task["completed"] = bool(data["completed"])
    if data.get("priority"):
        task["priority"] = data["priority"]

    return jsonify({"message": "Task updated successfully", "task": task})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task by ID."""
    global tasks
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    tasks = [t for t in tasks if t["id"] != task_id]
    return jsonify({"message": f"Task '{task['title']}' deleted successfully"})


@app.route("/api/tasks/<int:task_id>/toggle", methods=["PATCH"])
def toggle_task(task_id):
    """Toggle task completion status."""
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    task["completed"] = not task["completed"]
    status = "completed" if task["completed"] else "incomplete"
    return jsonify({"message": f"Task marked as {status}", "task": task})


# ============================================================
# SEARCH ENDPOINT
# ============================================================

@app.route("/api/search", methods=["GET"])
def search():
    """Search across all data. Requires ?q= query parameter."""
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    results = {
        "query": query,
        "users": [u for u in users if query in u["name"].lower() or query in u["email"].lower()],
        "products": [p for p in products if query in p["name"].lower() or query in p["category"].lower()],
        "tasks": [t for t in tasks if query in t["title"].lower()],
    }
    results["total_results"] = len(results["users"]) + len(results["products"]) + len(results["tasks"])
    return jsonify(results)


# ============================================================
# STATS ENDPOINT
# ============================================================

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get statistics about all data."""
    return jsonify({
        "users": {
            "total": len(users),
            "by_role": {
                "admin": len([u for u in users if u["role"] == "admin"]),
                "moderator": len([u for u in users if u["role"] == "moderator"]),
                "user": len([u for u in users if u["role"] == "user"]),
            }
        },
        "products": {
            "total": len(products),
            "in_stock": len([p for p in products if p["in_stock"]]),
            "out_of_stock": len([p for p in products if not p["in_stock"]]),
            "avg_price": round(sum(p["price"] for p in products) / len(products), 2) if products else 0,
            "categories": list(set(p["category"] for p in products)),
        },
        "tasks": {
            "total": len(tasks),
            "completed": len([t for t in tasks if t["completed"]]),
            "pending": len([t for t in tasks if not t["completed"]]),
            "by_priority": {
                "high": len([t for t in tasks if t["priority"] == "high"]),
                "medium": len([t for t in tasks if t["priority"] == "medium"]),
                "low": len([t for t in tasks if t["priority"] == "low"]),
            }
        }
    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found. Visit /api for available endpoints."}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed for this endpoint."}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error."}), 500


# ============================================================
# RUN THE APP
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("  Flask API Tutorial App")
    print("  Visit: http://localhost:5000")
    print("  API:   http://localhost:5000/api")
    print("=" * 50)
    app.run(debug=True, port=5000)
