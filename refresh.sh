rm -r app/static/mood_images/*
rm -r app/static/word_maps/*
rm -f test_data.db
sqlite3 test_data.db < .database_schema.sql