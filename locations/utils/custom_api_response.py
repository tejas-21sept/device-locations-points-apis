# For accessing standard HTTP status messages
import http.client

def get_status_message(status_code):
    """
    Returns the corresponding status message for a given HTTP status code.

    Args:
        status_code (int): The HTTP status code.

    Returns:
        str: The status message associated with the code.
    """
    return http.client.responses.get(status_code, "Unknown Status Code")


def api_response(status_code, message="", data=None):
    """
    Constructs a standardized API response dictionary with consistent structure.

    Args:
        status_code (int): The HTTP status code to include in the response.
        message (str, optional): An optional message to provide additional context. Defaults to an empty string.
        data (Any, optional): Optional data to be included in the response. Defaults to an empty list.

    Returns:
        dict: A dictionary containing the API response with the following structure:
            {
                "status": status_code,
                "data": data,
                "message": The corresponding status message for the status code,
            }
    """

    if data is None:
        data = []
    return {
        "status": status_code,
        "data": data,
        "message": message or get_status_message(status_code),
    }
