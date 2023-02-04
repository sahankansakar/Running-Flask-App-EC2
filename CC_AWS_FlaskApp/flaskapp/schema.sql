DROP TABLE IF EXISTS user;

CREATE TABLE user (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    firstname TEXT NOT NULL DEFAULT '',
    lastname TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    text_file TEXT NOT NULL DEFAULT ''
);
