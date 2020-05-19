"""created a table books in database"""
CREATE TABLE books (
id SERIAL PRIMARY KEY,
isbn VARCHAR NOT NULL,
title VARCHAR NOT NULL,
author VARCHAR NOT NULL,
publishyear VARCHAR NOT NULL
);


"""created another table for users"""
CREATE TABLE users (
id SERIAL PRIMARY KEY,
username VARCHAR NOT NULL,
email VARCHAR NOT NULL,
password VARCHAR NOT NULL
);


"""created another table which linked isbn numbers of books with users and their reviews"""
CREATE TABLE reviews (
id SERIAL PRIMARY KEY,
isbn VARCHAR,
username VARCHAR,
comments VARCHAR,
rating INTEGER
);
