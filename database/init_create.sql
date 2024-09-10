CREATE TABLE counters (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  tally INT NOT NULL
);

CREATE TABLE users (
  user_id INTEGER PRIMARY KEY,
  username VARCHAR(255) NULL,
);

CREATE TABLE lists (
  list_id INTEGER PRIMARY KEY,
  list_name VARCHAR(255) NOT NULL,
  list_items TEXT NOT NULL
);

CREATE TABLE user_lists (
  list_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  list_name VARCHAR(255) NOT NULL,
  list_items TEXT NOT NULL
);