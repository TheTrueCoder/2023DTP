class Book:
    checked_out = False

    def __init__(self, name: str, author: str = "Unknown", year_of_release: int = -1) -> None:
        self.name = name
        self.author = author
        self.year_of_release = year_of_release

class Library:
    books = {}
    members = {}

    def __init__(self, name = "New Library") -> None:
        self.library_name = name

    def add_book(self, book: Book) -> None:
        # try:
        keys = self.books
        keys = list(keys)
        i = max(keys)+1
        self.books[i] = book
        # except TypeError:
        #     self.books[1] = book

    def add_member(self, name: str) -> None:
        self.members[name] = []

    def checkout_book(self, member: str, book_id: int) -> bool:
        if self.books[book_id].checked_out is False:
            self.members[member].append(book_id)
            self.books[book_id].checked_out = True
            return True
        return False


library1 = Library("Nathan's lil library")

library1.add_book(Book("Harry Potter and the Order of the Phoenix", "J.K. Rowling", 2003))
library1.add_book(Book("The Hunger Games", "Suzanne Collins", 2008))

library1.add_member("Nathan")

library1.checkout_book("Nathan", 1)

print(library1.members)
print(library1.books)