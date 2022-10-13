# Anonymous Mood Board CS50 Project

The aim for this project was to create a web application which logged user data regarding their emotions on a scale from 1 - 10 (with 1 being the lowest) and provide an anonymous comparison with all other users on the platform through the display of informative charts. It also provides a 'word cloud' generator which shows the user a generalization of all of the words they used to describe their choice. Users then get to decide what the scale means for themselves. The project draws upon concepts and tools learnt through Harvard's [CS50 course](https://cs50.harvard.edu/x/2022/project/).

## 3rd party software
Quiet a few of these modules share dependencies. I only include here the modules from which I reference directly in my code. File names which are titles correspond to the modules I have made and that have been adapted from the CS50 course and other 3rd party software to suit the application. Namely, `authentication, free_apis, image_generator`.

#### main.py
- os
- secrets
- flask
- flask_session
- werkzeug.security
- cs50
- datetime
- re
#### authentication.py
- functools
- sre_parse
#### free_apis.py
- requests
- random
#### image_generator.py
- PIL
- wordcloud
- multidict
- matplotlib.pyplot

## Set up

Setting up to run the application depends on the following files and alterations which are either ignored by `.gitignore`, or won't exist on cloned versions. After the cloning of this repository and setting up the following files which exist in the root directory of the project folder, install 3rd party software in requirements.txt with `pip install -r requirements.txt`

#### .database_schema.sql *Database SQL*
```
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, hash TEXT NOT NULL, path_to_img TEXT NOT NULL, username TEXT NOT NULL, path_to_wc TEXT);
CREATE TABLE moods (user_id INTEGER NOT NULL, mood_id INTEGER PRIMARY KEY AUTOINCREMENT, date DATETIME DEFAULT CURRENT_TIMESTAMP, rating INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id));
CREATE TABLE mood_descriptions (fmood_id INTEGER NOT NULL, description TEXT NOT NULL, FOREIGN KEY (fmood_id) REFERENCES moods(mood_id));
CREATE VIEW daily_average AS SELECT strftime('%m-%d-%Y', date) AS fdate, COUNT(*) AS count, AVG(rating) as average_rating FROM moods GROUP BY fdate
/* daily_average(fdate,count,average_rating) */;
```

#### Shell Scripting *CLI command to run application with ease*

> In the .venv/bin/activate shell script
```
# create an alias for refresh.sh file
alias mood-board-start="bash refresh.sh"
echo "command for application: mood-board-start [true|false]"
```

## Configuration

Configuration includes environment files (.env variables displayed here do not reflect on any version of this application that is served via WSGI server), configuration files, as well as configuration that exists in main.py itself.

#### Environment Variables
For the project submission I will not include any hosts, ports or the like on my production server. These variables set the **bare minimum** for the application to run on localhost and Flask only.

```
TESTING_DATABASE="sqlite:///test_data.db"
CLIENT_DATABASE="sqlite:///test_data.db"
TEST_PORT="5001"
PRODUCTION_PORT="5650"
```

#### config.py
**LOG_LIMIT** sets an environment variable which helps restrict the amount of moods a user can log. The chosen limit is two logs per day.

**RGB_SCHEME_MAP** is the chosen colorscheme which corresponds to a user's chosen number.

```
# Configurations for limits / constants throughout the web application
# This is one day in seconds
LOG_LIMIT = 86400

# RGB scheme for user moods and other colours
RGB_SCHEME_MAP = {
    1: [57, 59, 87],
    2: [57 + (19 * 2), 59 + (17 * 2), 87 + (8 * 2)],
    3: [57 + (19 * 3), 59 + (17 * 3), 87 + (8 * 3)],
    4: [57 + (19 * 4), 59 + (17 * 4), 87 + (8 * 4)],
    5: [57 + (19 * 5), 59 + (17 * 5), 87 + (8 * 5)],
    6: [57 + (19 * 6), 59 + (17 * 6), 87 + (8 * 6)],
    7: [57 + (19 * 7), 59 + (17 * 7), 87 + (8 * 7)],
    8: [57 + (19 * 8), 59 + (17 * 8), 87 + (8 * 8)],
    9: [57 + (19 * 9), 59 + (17 * 9), 87 + (8 * 9)],
    10: [57 + (19 * 10), 59 + (17 * 10), 87 + (8 * 10)],
}
```

#### refresh.sh

This file reads the command line argument for the alias `mood-board-start` and determines how to run the application. "true" means that the application will run tests and then close down, "false" means that the application is running in production.

The FLASK_APP variable and the port number depends simply on the true|false from the command line. The value of FLASK_APP takes the value returned form a function withing *main.py* and is either set to `"app.main:create_app(test=True)"` or `"app.main:create_app(test=False)"`.

***On a production server I would use gunicorn and update this script accordingly.***

```
install_cont() {
    # Declare local command of [true|false]
    local expres="$1"

    # Get the testing and production ports to run flask/gunicorn to enable testing while in production.
    local test_port="$(dotenv get "TEST_PORT")"
    local production_port="$(dotenv get "PRODUCTION_PORT")"

    # If the command == true export the FLASK_APP variable to run tests
    if [ "$expres" == "true" ]; then
        export FLASK_APP="app.main:create_app(test=True)"
        # Only use these commands if testing requires a full swipe of image data
        # Both the test and production applications will use the same folder
        # rm -r app/static/mood_images/*
        # rm -r app/static/word_maps/*
        # rm -r flask_session

        # Remove the testing database and create a new one.
        rm -f test_data.db
        sqlite3 test_data.db < .database_schema.sql

        # Run on the testing port and output the tests to a file
        flask run -p $test_port &
        sleep 5; pytest > tests/test_output.txt

        # Kill the process serving the testing application on the testing port
        fuser -k $test_port/tcp
        printf "\n\nTest completed! see tests/test_output.txt"
    else
        export FLASK_APP="app.main:create_app(test=False)"
        flask run -p $production_port
    fi
}
install_cont "$1"
```
## Testing files

## Python Custom modules

## The app Folder
#### static
#### templates
#### main.py