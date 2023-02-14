from typing import Dict, List

class Book:
    checked_out = False

    def __init__(self, name: str, author: str = "Unknown", year_of_release: int = -1) -> None:
        self.name = name
        self.author = author
        self.year_of_release = year_of_release

class Library:
    books: Dict[int, Book] = {}
    members: Dict[str, List[int]] = {}
    _new_book_index = 1

    def __init__(self, name = "New Library") -> None:
        self.library_name = name

    def add_book(self, book: Book) -> None:
        self.books[self._new_book_index] = book
        self._new_book_index += 1
    
    def add_member(self, name: str) -> None:
        self.members[name] = []

    def checkout_book(self, member: str, book_id: int) -> bool:
        if self.books[book_id].checked_out is False:
            self.members[member].append(book_id)
            self.books[book_id].checked_out = True
            return True
        return False

    def return_book(self, book_id: int) -> bool:
        if self.books[book_id].checked_out is True:
            for user, book_ids in self.members:
                if book_id in book_ids:
                    self.members[user][book_ids.find(book_id)]


natlib = Library("Nathan's lil library")

natlib.add_book(Book("Harry Potter and the Order of the Phoenix", "J.K. Rowling", 2003))
natlib.add_book(Book("The Hunger Games", "Suzanne Collins", 2008))

natlib.add_member("Nathan")

natlib.checkout_book("Nathan", 1)

print(natlib.members)
print(natlib.books)