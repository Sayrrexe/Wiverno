from wiverno.main import MethodNotAllowed405

class BaseView:
    
    def __call__(self, request):
        handler = getattr(self, request.method.lower(), None)
        if handler:
            return handler(request)
        
        handler_405 = MethodNotAllowed405()
        return handler_405(request)