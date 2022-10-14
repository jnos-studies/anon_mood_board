import requests
from dotenv import load_dotenv
import os

def test_endpoints():
    # load environment variables
    load_dotenv()
    
    # Open a test process using localhost to test the endpoints, that they redirect to login
    PORT = os.environ.get("TEST_PORT")
    testing_port = f"http://127.0.0.1:{PORT}/"
    end_points = [ "register", "login", "all_moods", "", "log_mood"]

    # Store status codes to be checked
    status_codes = []
    
    for r in end_points:
        print("checking {}".format(testing_port + r))
        status_codes.append(requests.get(testing_port + r).history)
    
    status_string = str(status_codes)
    assert status_string == "[[], [], [<Response [302]>], [<Response [302]>], [<Response [302]>]]"