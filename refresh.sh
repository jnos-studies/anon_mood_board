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
         rm -r app/static/mood_images/*
         rm -r app/static/word_maps/*
         rm -r flask_session

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