import json
from typing import Dict, Any
from urllib.parse import parse_qs
from email.parser import BytesParser
from email.policy import default

class GetRequest:

    @staticmethod
    def parse_input_data(data: str) -> dict:
        """
        Parses the input data from a GET request query string into a dictionary.
        
        :param data: The query string from the GET request.
        :return: A dictionary with key-value pairs from the query string.
        """
        if not data:
            return {}
        
        # Split the query string into key-value pairs
        pairs = data.split('&')
        result = {}
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=')
                result[key] = value
            else:
                result[pair] = None
        return result
    
    @staticmethod
    def get_request_params(environ: dict) -> dict:
        """
        Retrieves and parses the query string from the WSGI environment.
        
        :param environ: The WSGI environment dictionary.
        :return: A dictionary with parsed query parameters.
        """
        query_string = environ.get('QUERY_STRING', '')
        return GetRequest.parse_input_data(query_string)
    
class PostRequest:
    """
    Handles parsing of POST request data from the WSGI environment.
    Supports: multipart/form-data, application/x-www-form-urlencoded, application/json.
    """

    def get_request_params(self, environ: dict) -> Dict[str, Any]:
        """
        Parses POST request data from the WSGI environment.

        Args:
            environ (dict): The WSGI environment.

        Returns:
            dict: Parsed POST data.
        """
        content_type: str = environ.get('CONTENT_TYPE', '')
        content_length: int = int(environ.get('CONTENT_LENGTH', 0))
        wsgi_input: bytes = environ['wsgi.input'].read(content_length)

        if content_type.startswith('multipart/form-data'):
            boundary = content_type.split('boundary=')[-1]
            content: bytes = b'Content-Type: ' + content_type.encode() + b'\r\n\r\n' + wsgi_input
            msg = BytesParser(policy=default).parsebytes(content)

            data: Dict[str, Any] = {}
            for part in msg.iter_parts():
                name = part.get_param('name', header='content-disposition')
                if name:
                    data[name] = part.get_content()
            return data

        elif content_type == 'application/x-www-form-urlencoded':
            return {k: v[0] for k, v in parse_qs(wsgi_input.decode()).items()}

        elif content_type == 'application/json':
            return json.loads(wsgi_input.decode())

        return {}