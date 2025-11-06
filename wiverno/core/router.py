from typing import Callable, List, Optional, Dict


class Router:
    def __init__(self) -> None:
        self._routes: List[Dict] = []
    
        
    def route(self, path: str, methods: Optional[List[str]] = None):
        def decorator(func):
            self._routes.append({
                'path': path,  
                'handler': func,  
                'methods': methods or ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
            })
            return func
        return decorator
    
    def get(self, path: str):
        return self.route(path, methods=['GET'])
    
    def post(self, path: str):
        return self.route(path, methods=['POST'])
    
    def put(self, path: str):
        return self.route(path, methods=['PUT'])
    
    def patch(self, path: str):
        return self.route(path, methods=['PATCH'])
    
    def delete(self, path: str):
        return self.route(path, methods=['DELETE'])
    
    def connect(self, path: str):
        return self.route(path, methods=['CONNECT'])
    
    def head(self, path: str):
        return self.route(path, methods=['HEAD'])
    
    def options(self, path: str):
        return self.route(path, methods=['OPTIONS'])
    
    def trace(self, path: str):
        return self.route(path, methods=['TRACE'])
    
    def add_route(self, path: str, handler: Callable, methods: Optional[List[str]] = None):
        self._routes.append({
            'path': path,
            'handler': handler,
            'methods': methods
        })
        
        