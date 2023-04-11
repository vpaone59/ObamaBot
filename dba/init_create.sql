CREATE SCHEMA obama;

USE obama;

CREATE TABLE counters (
  id INT NOT NULL AUTO_INCREMENT,
  name_of_counter VARCHAR(255) NOT NULL,
  tally_counter INT NOT NULL,
  PRIMARY KEY (id)
);
