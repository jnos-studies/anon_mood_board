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

Configuration includes environment files. *.env variables displayed here do not reflect on any version of this application that is served via WSGI server*, configuration files, as well as configuration that exists in main.py itself.

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
There are only two tests that exist in the tests folder which tests how my application escapes characters and also ensures http requests to any endpoint without a valid session cookie will return a 302 and redirect to the login page.
#### test_character_escaping.py
The sre_parse is a builtin python library that is imported through `authentication.py` and is used in this test to escape special characters via `sre_parse.SPECIAL_CHARACTERS` by converting any special character existing in user input into a regular expression which tests whether the input only contains alphabetic characters. This way, any user input regarding the logging of words into the database is cleansed of illegal characters that might make my databases vulnerable to SQL injection.
```
def test_conversion_to_regexp():
    # properly reject's input if it contains a space, digit, or backspace character after performing escapes
    # on sre_parsed characters.
    r_pattern_true = convert_to_regexp("test")
    r_pattern_false = convert_to_regexp("a b c")
    truthy = r_pattern_true.isalpha()
    falsey = r_pattern_false.isalpha()

    assert truthy == True and falsey == False, "Properly rejects input that is not a single word"
```

#### test_endpoints.py
As mentioned before, this will test all of my applications endpoints and ensure that a 302 redirects the user to the login page if there exists no valid session cookie for the user. It takes the `TESTING_PORT` environment variable and reads it's history to determine that each endpoint has returned a 302 successfully.
```
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
```
#### test_output.txt
Test results will be written into this text file displaying what passed and what failed. I chose to output the results to a file in order to use this file to enable easy implementation of emailing tests to myself in the future, automatically.

## Python Custom modules

#### authentication.py
This module utilizes the builtin `sre_parse` and `functools` library to perform authentication measures for user login.
##### convert_to_regexp
Converts user input to regular expression to ensure no illegal characters which may cause my application vulnerable to SQL injection impossible, as far as I know.
##### apology
Taken from the CS50 course it renders an error page which displays the error and an amusing picture of grumpy cat to inform the user of unauthorized actions from the client side. Implemented in `main.py`. It also escapes special characters without using the `sre_parse` builtin.
```
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code
```

##### login_required
Also taken from the CS50 course. This is a decorator function that ensures all critical endpoints returned by http responses in `main.py` contain a valid session cookie. 
#### free_apis.py
A very simple module which handles GET requests to [this quote generator](ttps://type.fit/api/quotes) to display a motivational quote to the user on their homepage. It uses the random module to achieve the sudo-random selection of a quote returned by the GET requests

```
def get_random_quote():
    resp = get("https://type.fit/api/quotes")
    data = resp.json()
    quotes_all = len(data)
    random_quote = data[random.randrange(quotes_all)]
    return random_quote
```
#### image_generator.py
The most involved module I made which uses the [Pillow](https://pypi.org/project/Pillow/) imaging library and the [wordcloud](https://pypi.org/project/wordcloud/) library to generate custom images for both the user 'mood image' and a word cloud which takes from the database to display the users most used words. The wordcloud library uses `multidict` and `matplotlib.pyplot` to map out words which the user has logged by order of frequency, this creates images such as the following,
![Word cloud image](http://res.cloudinary.com/dyd911kmh/image/upload/f_auto,q_auto:best/v1530034171/Aromas_bfy0ec.png)

Mood images are stored in the `static/mood_images/` folder, and wordclouds are stored in the `static/word_maps/` folder after their file names/locations have been entered into the database to retrieve user-specific images later.

##### make_mood_image
Takes a string value `name` and list value `rgb` to save a newly created user's mood image into the `mood_images` folder under the respective name.
The size of the image is 32 x 32 pixels to account for memory. Each image is 101 bytes.
```
def make_mood_image (name, rgb):
    if isinstance(rgb,list):
        new = Image.new(mode="RGB", size=(32,32), color=(rgb[0], rgb[1], rgb[2]))
        print("test")
        new.save(f"app/static/mood_images/{name}.png")
    else:
        return 1
```
##### getFrequencyDictForText
Taken from an example on wordcloud's [documentation](https://github.com/amueller/word_cloud/blob/master/examples/frequency.py) this function uses the `multidict` library to measure the frequency of words that has been logged into the database by the user over time. It takes a string of text, splits it into an array, then uses the builtin `re` library to ignore any words that are english prepositions. The end result is a dictionary that contains each individual word and the frequency it appears. *Does not take misspellings into account.*
```
def getFrequencyDictForText(sentence):
    fullTermsDict = multidict.MultiDict()
    tmpDict = {}

    # making dict for counting frequencies
    for text in sentence.split(" "):
        if re.match("a|the|an|the|to|in|for|of|or|by|with|is|on|that|be", text):
            continue
        val = tmpDict.get(text, 0)
        tmpDict[text.lower()] = val + 1
    for key in tmpDict:
        fullTermsDict.add(key, tmpDict[key])
    return fullTermsDict
```

##### makeImage and make_word_cloud
Both functions are used in tandem to create the word cloud and save it into a file. `make_word_cloud` takes the data generated by `getFrequencyForDict`, converts each word into lowercase, and calls `make_image` to plot the words on a matrix and save it as a png file under the given `name` variable.
```
def makeImage(name, text):
    wc = WordCloud(background_color="white", max_words=1000)
    # generate word cloud from frequency of word
    wc.generate_from_frequencies(text)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(name + ".png")
    
def make_word_cloud (name, data):
    data_text = ""
    for word in data:
        data_text += word["description"] + " "
    data_text.lower()
    makeImage(name, getFrequencyDictForText(data_text))
```

## The app Folder
This folder is structured as is required by Flask's [documentation](https://flask.palletsprojects.com/en/2.2.x/tutorial/layout/).
#### static
Contains all javascript, mood images, css, and word clouds used by my application. It also includes the [menu-icon.png](/app/static/menu-icon.png) image and the [favicon.ico](/app/static/favicon.ico) image.
##### The js folder
###### logged_moods.js
Sets the style for each table row icon's background color on `log_mood.html` which represents the color of the users selected on the user's home page. Each table row shares the `class="mood"` attribute, as well as a `value` attribute that is rendered in main.py. This allows an accurate representation of what the user selected at a given time.
###### select_mood.js
Creates an event listener on the `log_mood.html` page which animates and changes the color of the radio buttons which the user selects, as well as changing the background color of the div element with the id `mood-select-color` to represent the current choice the user will make before logging their mood. All changes in colors correspond to the users selected mood and the predetermined rgb values which are mapped to the values 1-10.
#### templates, styles, and mood representation
Templates are rendered using the Jinja templating engine which is downloaded with `Flask`. I will only include here html pages that deserve an explanation of design choices. Styling of html elements are provided by the [Bootstrap](https://getbootstrap.com/) library, as well as [custom css](/app/static/styles.css).

Custom css is only used to fine-tune elements to fit properly on the page, and to provide default color values before they are changed by javascript. On the same note, my stylistic choices leaned towards a simple colorscheme of pastels to convey the changes in a persons mood over time. As the user interacts with the application their mood image changes color. The rgb balues of the mood image itself is generated by taking the user's average mood through all time and providing a color that is unique to them, but also comparible to other users. This image is the centerpiece of the application and is outlined by an animated border that changes color on an animated gradient, representing how moods change.

>Animated gradient for the border surrounding the user's mood image. Using keyframe css animations the following css basically blows up a gradient image and changes its position in a loop to achieve the desired effect.
```
#user_image {
    width: 100px;
    height: 100px;
  }

#user_image_bg {
  position: relative;
  width: 150px;
  height: 150px;
  background-color: rgba(215, 54, 92, 0.7);
  transition: background-color .1s;
  content: '';
  background: linear-gradient(45deg, rgb(97, 101, 148), rgb(213, 255, 232), rgb(247, 235, 171));
  background-size: 200% 200%;
  background-position: 0% 150%;
  animation-name: test_hover;
  animation-duration: 4s;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
  animation-direction: alternate;
  margin: auto;
  padding: 25px;
  border-radius: 10%;
}

...

@keyframes test_hover {
  from {
    background-position: 0% 100%;
  }
  to {
    background-position: 100% 0%;
  }
}
```

##### layout.html
The layout of every html page, it contains the navigation bar which exists throughout the whole application excepting the login and registration pages. It displays any flash messages returned from the back end and only renders the navigation bar if the user contains a valid session login cookie. It will render a different navigation bar to navigate to the user login and registration.

```
 {%if session["user_id"]%}
        <nav class="nav" style="height:10px;"></nav>
        ...
        {% else %}
        <nav class="nav" style="width: 100%;">
            <a class="flex-sm-fill text-sm-center nav-link emotive" aria-current="page" href="/login">login</a>
            <a class="flex-sm-fill text-sm-center nav-link emotive" href="/register">register</a>
        </nav>
        {% endif %}
```

##### index.html
Uses the `logged_moods.js` file as a script to perform what was previously aforementioned in the description of the file, display a random motivational quote, and to display the current version of the users mood image and word cloud. Both the mood image and word cloud are always up-to-date as their files are overwritten every time a user logs a mood.

In this file the Jinja engine will ensure that the word cloud will only appear if one exists for the current user.
```
 {% if path_to_wc %}
        <div id="wordcloud" class="text-center container-fluid">
            <img src={{ path_to_wc }} alt="Your wordcloud" class="img-fluid" width="80%" border-radius="10%">
        </div>
    {% endif %}
```
This was to fix a bug that rendered the image `src` attribute with nothing to refer to.

##### all_moods.html
I wanted a way for the user to see how their moods compare with other users statistically. Utilizing the [Chart.js](https://www.chartjs.org/) library enables a website to easily implement data in several different types of charts.

I hardcoded a script within the html page which creates a bar chart representing proportion of the users mood-choices compared with other users who chose the same number, and a line chart which shows the fluctuations of the users mood through time compared to other users.

The data is rendered through the jinja engine into a `<data>` element which is used by the script to display the data. To measure differences between the user's data compared to other's, I made a function that returns an array detailing those differences by subtracting the user's choices from the entire dataset.

```
function difference(arr, arr2)
    {
      let new_arr = [];
      for (let i = 0; i < arr.length; i++)
      {
        new_arr.push(arr[i] - arr2[i])
      }
      return new_arr
    }
```

##### apology.html, log_mood.html, login.html, and register.html
These html files only require a summary of what they are and what they do.

- [apology.html](/app/templates/apology.html) was taken from the CS50 course and was part of [problem set 9](https://cs50.harvard.edu/x/2022/psets/9/) on creating Flask applications.
- [log_mood.html](/app/templates/log_mood.html) is a more complex form that sends post requests to the backend server which contain data about the users choice of mood, and a word representing their mood. Uses the [select_mood.js](/app/static/js/select_mood.js) script to perform what was aforementioned in the previous section.
- [loging.html](/app/templates/login.html) is a simple form which handles user login, sends post requests to backend server.
- [register.html](/app/templates/register.html) is a simple form which handles user registration, sends post requests to backend server.

#### main.py
This section will detail choices for handling data in the back end and what happens at specific endpoints.

##### @app.after_request
Sets the program to not cache any cookies that come from http responses.

```
def after_request(response):
        # Ensure responses are not cached
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"

        return response
```
##### @app.route("/")
This endpoint accesses user information from the database and pulls information that was created during the registration process. It gathers the file paths to both the user's mood image and word cloud, as well as all of the user's logged moods and renders them in a html table. It also pulls a quote using the free_api module to diplay on the page, it then renders all of this information to the index.html page.
```
  return render_template("index.html",\
            image_path=user_image_path,\
            username=username[0]["username"],\
            moods=reverse_moods, rgb=config.RGB_SCHEME_MAP,\
            quote_text=inspirational_quote['text'],\
            quote_author=inspirational_quote['author'],\
            path_to_wc=wc_path_to)
```

##### @app.route("/log_mood")
Gets information from the database to render things like the number of moods the user has logged already. It also checks that the most recent user log has not exceeded 2 the daily limit. It uses the `LOG_LIMIT` environment variable and compares the last most logged mood with the most recent date. The difference between the values within the `timedeltas` list cannot exceed the limit.

```
 # For checking the log limit, reject request if user exceeds their daily limit
        current_date = date.now()
        limit = config.LOG_LIMIT
        timedeltas = ""
        # Limit is defined in seconds for accuracy. Check that the last two logs are within limit, if number of logs is less than 2, timedelta equals the limit, allowing log of moods
        if num_logged_moods >= 2:
            timedeltas = [(current_date - date.strptime(moods[-2:][0]["date"],"%Y-%m-%d %H:%M:%S")).total_seconds(), (current_date - date.strptime(moods[-2:][1]["date"],"%Y-%m-%d %H:%M:%S")).total_seconds()]
        else:
            timedeltas = [limit, limit]
    
```
In the subsequent post request to the database it compares the timedeltase,
```
if timedeltas[0] < limit and timedeltas[1] < limit:
                next_log = round(limit - timedeltas[1])
                flash("You can only log 2 moods per day! Time until next available log is {} seconds, {} minutes, or {} hours!!".format(next_log, round(next_log / 60, 2), round((next_log / 60) / 60), 2))
```
If the user logging has not exceeded the log limit it then updates the database, and overwrites the users passed mood image and word cloud to reflect the most current data. It takes user input from the radio buttons and the text input as data sent through the POST request. Text input is sanitized with the `convert_to_regex` function which converts the text input into a regular expression that will produce illegal characters if the user has used any. Text is required to be purely alphabetic and without spaces.

```
if r_pattern.isalpha() == False or len(emot_description) > 15:
                    flash("Only single word descriptions of your mood are allowed!")
                    return redirect("/log_mood")
```

##### @app.route("/all_moods")
Gathers information from the database and performs calculations which compare the user's most picked and averaged moods and compares them with others. It renders the values needed for the chart.js library to render charts and graphics from the script written in [all_moods.html](/app/templates/all_moods.html).

It will only render the average user data compared to what the user has picked themselves, ie: compare how many people picked the number 10 as compared to the user on a particular day.

```
daily_avg_user = db.execute("SELECT strftime('%m-%d-%Y', date) AS fdate, COUNT(*) AS count, AVG(rating) as average_rating FROM moods WHERE user_id = ? GROUP BY fdate;", session["user_id"])
        dau_x = [a["fdate"] for a in daily_avg_user]
        dau_y = [a["average_rating"] for a in daily_avg_user]
        # Get the averate user ratings for every user which logged a mood the same day as the logged user.
        daily_avg_all = db.execute("SELECT * FROM daily_average WHERE fdate IN (SELECT strftime('%m-%d-%Y', date) AS fdate FROM moods WHERE user_id = ? GROUP BY fdate)", session["user_id"])
        daa_x = [a["fdate"] for a in daily_avg_all if a["fdate"]]
        daa_y = [a["average_rating"] for a in daily_avg_all]
```

##### @app.route("/login")
A simple single factor sign in which checks that a user exists and that their password matches with the hashed values in the database.

```
# Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")) or not len(request.form.get("username")) < 15:
                return apology("Invalid username and/or password!", 403)

            session["user_id"] = rows[0]["id"]
            flash("Logged in successfully.")
```

##### @app.route("/logout")
Logs the user out by clearing their associated cookie with `session.clear()`.

##### @app.route("/register")
A simple registration, it will handle post requests which checks that the username entered does not contain any illegal characters and is below the length of 10. It also enforces password restrictions by using regular expressions for password validation,

It then inserts data sent by the post request into the database and creates the new user's mood image which defaults to the lowest value in the `RGB_SCHEME` environment variable.

```
if request.method == "POST":
            username, password, confirmation = request.form.get(
                "username"), request.form.get("password"), request.form.get("confirmation")
             # Only allow certain characters for username, sanitize user input

            if len(username) > 10:
                return apology("Your chosen username should not be longer than 10 characters")
            for i in illegal_chars:
                for c in username:
                    if i == c:
                        return apology(f"Character's not allowed! {illegal_chars}")
            # Check if the password matches and if the user exits.
            if password == confirmation:
                user_exists = db.execute("SELECT * FROM users WHERE username = ?;", username)
                # using regex for password validation, taken from https://uibakery.io/regex-library/password-regex-python
                """
                    Has minimum 8 characters in length. Adjust it by modifying {8,}
                    At least one uppercase English letter. You can remove this condition by removing (?=.*?[A-Z])
                    At least one lowercase English letter.  You can remove this condition by removing (?=.*?[a-z])
                    At least one digit. You can remove this condition by removing (?=.*?[0-9])
                    At least one special character,  You can remove this condition by removing (?=.*?[#?!@$%^&*-])
                """
                password_validation = (re.search("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$", password) == None)
                print(password_validation)
                if password_validation == True:
                    flash("""Password must be a minimum of 8 characters in length,
Have at least one uppercase English letter,
have least one lowercase English letter,
and have at least one digit.""")
                    return redirect("/register")

                if len(user_exists) == 0:
                    image_path = secrets.token_hex(16)
                    moodI(image_path, rgb=[57, 59, 87])
                    db.execute("INSERT INTO users (username, hash, path_to_img) VALUES(?, ?, ?)", username, generate_password_hash(password), image_path)
                    return redirect("/login")
                else:
                    return apology("User already exists!")
            else:
                return apology("Passwords do not match!")
                   
```