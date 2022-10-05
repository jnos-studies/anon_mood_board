import requests

def test_endpoints():
    # Open a test process using localhost to test the endpoints, that they redirect to login
    testing_port = "http://127.0.0.1:5000/"
    end_points = [ "register", "login", "all_moods", "", "log_mood"]

    # Store status codes to be checked
    status_codes = []
    
    for r in end_points:
        print("checking {}".format(testing_port + r))
        status_codes.append(requests.get(testing_port + r).history)
    
    status_string = str(status_codes)
    assert status_string == "[[], [], [<Response [302]>], [<Response [302]>], [<Response [302]>]]"