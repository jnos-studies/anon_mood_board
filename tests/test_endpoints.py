import requests
import os
import signal
import subprocess

def test_endpoints():
    # Open a test process using localhost to test the endpoints
    open_test = subprocess.Popen(["flask", "run --debug -h localhost -p 5550"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True)

    stdout, stderr = open_test.communicate()
    stdout, stderr

    
    print("flask testing app running on port 5550, pid {}".format(open_test.pid))
    # Send a signal terminate to all process groups and close the testing
    
test_endpoints()