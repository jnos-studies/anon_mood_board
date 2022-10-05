rm -r app/static/mood_images/*
rm -r app/static/word_maps/*
rm -f test_data.db
sqlite3 test_data.db < .database_schema.sql
rm -r flask_session

if echo $1 == "True"
then
    export FLASK_APP="app.main:create_app(test=True)"
    flask run
else
    export FLASK_APP="app.main:create_app(test=False)"
    flask run
fi