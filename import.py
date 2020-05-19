import csv

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
Session = scoped_session(sessionmaker(bind=engine))
db = Session()


def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, publishyear in reader:
        db.execute("INSERT INTO books(isbn, title, author, publishyear) VALUES (:isbn, :title, :author, :publishyear)",
                   {"isbn": isbn, "title": title, "author": author, "publishyear": publishyear})
        print(f"Added book with isbn {isbn}, title {title}, author {author} and publishyear {publishyear} to books.")
    db.commit()


if __name__ == '__main__':
    main()
