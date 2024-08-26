from fastapi import FastAPI

from api.utils.middleware.get_all_routes import get_all_routes

def test_get_all_routes():
    app = FastAPI()

    @app.get("/")
    async def read_root():
        return {"Hello": "World"}

    @app.get("/items/{item_id}")
    async def read_item(item_id: int):
        return {"item_id": item_id}

    @app.post("/items/")
    async def create_item():
        return {"item": "Created"}

    # Use the function to get all routes
    routes = get_all_routes(app)
    routes_filtered = [route for route in routes if route not in ['/openapi.json', '/docs', '/docs/oauth2-redirect', '/redoc']]

    # Test if all expected routes are present
    expected_routes = ["/", "/items/{item_id}", "/items/"]
    assert set(routes_filtered) == set(expected_routes), f"Routes do not match. Expected {expected_routes}, but got {routes_filtered}"