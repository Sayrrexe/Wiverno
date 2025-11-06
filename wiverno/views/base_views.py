from wiverno.main import MethodNotAllowed405

class BaseView:
    """
    Base class for class-based views.

    Subclasses should implement methods named after HTTP methods (get, post, put, etc.)
    to handle different request types. If a method is not implemented, a 405 error
    is returned.

    Example:
        class MyView(BaseView):
            def get(self, request):
                return '200 OK', '<html>GET response</html>'

            def post(self, request):
                return '201 CREATED', '<html>POST response</html>'
    """

    def __call__(self, request):
        """
        Dispatches the request to the appropriate HTTP method handler.

        Args:
            request (Request): The incoming request object.

        Returns:
            tuple[str, str]: A tuple of (status, html_body).
        """
        handler = getattr(self, request.method.lower(), None)
        if handler:
            return handler(request)

        handler_405 = MethodNotAllowed405()
        return handler_405(request)