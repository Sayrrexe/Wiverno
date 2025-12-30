from http import HTTPStatus

from wiverno.core.exceptions import InvalidHTTPStatusError


class HTTPStatusValidator:
    """
    Utility class for validating and normalizing HTTP status values.

    Converts an HTTP status code provided as an integer or string
    into a standardized string representation suitable for WSGI responses.
    """

    @staticmethod
    def normalize_status(status: int | str) -> str:
        """
        Normalize an HTTP status code to standard WSGI format.

        Accepts status codes as integers (e.g., 200), numeric strings (e.g., "404"),
        or strings with reason phrases (e.g., "200 OK") and converts them to the
        standardized format: "<status_code> <reason_phrase>".

        Args:
            status: HTTP status code as an integer (e.g. 200),
                   a numeric string (e.g. "404"),
                   or a string containing code and reason phrase (e.g. "200 OK").

        Returns:
            Normalized HTTP status string in the format
            "<status_code> <reason_phrase>" (e.g., "200 OK", "404 Not Found").

        Raises:
            InvalidHTTPStatusError:
                If the input cannot be interpreted as an HTTP status code.
            ValueError:
                If the HTTP status code is not recognized in the HTTP standard.

        Examples:
            >>> HTTPStatusValidator.normalize_status(200)
            '200 OK'
            >>> HTTPStatusValidator.normalize_status("404")
            '404 Not Found'
            >>> HTTPStatusValidator.normalize_status("201 Created")
            '201 Created'
        """
        if isinstance(status, int):
            code = status

        elif isinstance(status, str):
            parts = status.strip().split(maxsplit=1)

            if not parts or not parts[0].isdigit():
                raise InvalidHTTPStatusError(status)

            code = int(parts[0])

        else:
            raise InvalidHTTPStatusError(status)

        try:
            phrase = HTTPStatus(code).phrase
        except ValueError:
            raise ValueError(f"Unknown HTTP status code: {code}") from None

        return f"{code} {phrase}"


