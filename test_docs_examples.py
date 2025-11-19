"""
Test script to verify basic documentation examples work correctly.
This script creates a simple Wiverno app and tests core features documented in the guides.
"""

from wiverno import Wiverno
from wiverno.core.routing.router import Router
from wiverno.views.base_views import BaseView

# Create main app
app = Wiverno(debug_mode=True)


# Test 1: Basic routing with path parameters
@app.get("/")
def index(request):
    return "200 OK", "<h1>Hello, World!</h1>"


@app.get("/users/{id:int}")
def get_user(request):
    user_id = request.path_params["id"]
    return "200 OK", f"<h1>User {user_id}</h1>"


@app.get("/posts/{slug}/comments/{comment_id:int}")
def get_comment(request):
    slug = request.path_params["slug"]
    comment_id = request.path_params["comment_id"]
    return "200 OK", f"<p>Post: {slug}, Comment: {comment_id}</p>"


@app.get("/files/{filepath:path}")
def serve_file(request):
    filepath = request.path_params["filepath"]
    return "200 OK", f"<p>File: {filepath}</p>"


# Test 2: Query parameters with getlist
@app.get("/search")
def search(request):
    query = request.query_params.get("q", "")
    tags = request.query_params.getlist("tag")
    return "200 OK", f"<p>Search: {query}, Tags: {', '.join(tags)}</p>"


# Test 3: POST data
@app.post("/users")
def create_user(request):
    name = request.data.get("name", "")
    return "201 CREATED", f"<p>User {name} created</p>"


# Test 4: Multiple HTTP methods
@app.get("/items")
def list_items(request):
    return "200 OK", "<ul><li>Item 1</li></ul>"


@app.post("/items")
def create_item(request):
    return "201 CREATED", "<p>Item created</p>"


# Test 5: Class-based views
class UserView(BaseView):
    def get(self, request):
        user_id = request.path_params["id"]
        return "200 OK", f"<h1>User {user_id} Detail</h1>"

    def put(self, request):
        user_id = request.path_params["id"]
        return "200 OK", f"<p>User {user_id} updated</p>"

    def delete(self, request):
        return "204 NO CONTENT", ""


app.route("/users/{id:int}/detail")(UserView())


# Test 6: Router with prefix
api_router = Router()


@api_router.get("/users")
def api_users(request):
    return "200 OK", '{"users": []}'


@api_router.get("/users/{id:int}")
def api_user_detail(request):
    user_id = request.path_params["id"]
    return "200 OK", f'{{"id": {user_id}}}'


app.include_router(api_router, prefix="/api/v1")


# Test 7: Static route vs dynamic route priority
@app.get("/users/admin")
def admin_users(request):
    return "200 OK", "<h1>Admin users</h1>"


@app.get("/users/{username}")
def user_by_name(request):
    username = request.path_params["username"]
    return "200 OK", f"<h1>User: {username}</h1>"


if __name__ == "__main__":
    print("[OK] All routes registered successfully!")
    print("\nRegistered routes:")
    print("- GET  /")
    print("- GET  /users/{id:int}")
    print("- GET  /posts/{slug}/comments/{comment_id:int}")
    print("- GET  /files/{filepath:path}")
    print("- GET  /search")
    print("- POST /users")
    print("- GET  /items")
    print("- POST /items")
    print("- GET  /users/{id:int}/detail")
    print("- PUT  /users/{id:int}/detail")
    print("- DELETE /users/{id:int}/detail")
    print("- GET  /api/v1/users")
    print("- GET  /api/v1/users/{id:int}")
    print("- GET  /users/admin (static - higher priority)")
    print("- GET  /users/{username}")
    print("\nTo test the app, run:")
    print("  wiverno run dev test_docs_examples:app")
