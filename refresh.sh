if echo $1 == "True"
then
    export FLASK_APP="app.main:create_app(test=True)"
    rm -r app/static/mood_images/*
    rm -r app/static/word_maps/*
    rm -f test_data.db
    sqlite3 test_data.db < .database_schema.sql
    rm -r flask_session

    flask run &
    sleep 5; pytest > tests/test_output.txt
    fuser -k 5000/tcp
    printf "\n\nTest completed! see tests/test_output.txt"
else
    export FLASK_APP="app.main:create_app(test=False)"
    flask run
fi