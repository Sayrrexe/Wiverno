class PageNotFound404:
    def __call__(self):
        return "404 WHAT", "Page not found"
    
class Wiverno:
    
    def __init__(self, routes_list):
        self.routes_list = routes_list
    
    def __call__(self, environ, start_response):
        # Extract the path from the environment
        path = environ['PATH_INFO']
        
        
        # add close /
        if not path.endswith('/'):
            path = path + '/'
            
        # see if the path matches any route
        if path in self.routes_list:
            view = self.routes_list[path]
        else:
            view = PageNotFound404()

        # start the controller
        code, body = view()
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]