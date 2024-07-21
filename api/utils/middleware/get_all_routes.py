from typing import List
from fastapi import FastAPI

def get_all_routes(app: FastAPI) -> List[str]:
    paths = []
    for route in app.routes:
        paths.append(route.path)
    return paths