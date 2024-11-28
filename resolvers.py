from ariadne import QueryType,MutationType, SubscriptionType
from models import Author,Book
from flask_cors import CORS
from flask import Flask, g
from banco import gravarAuthorDB, gravarBookDB
import asyncio
from asyncio import get_event_loop
from starlette.websockets import WebSocket

app = Flask (__name__)
CORS (app)


authors_db = []
books_db = []

query = QueryType()
mutation = MutationType()
subscription = SubscriptionType()

@query.field("authors")
def resolve_authors(_,info):
    return authors_db

@query.field("books")
def resolve_books(_,info):
    return books_db

@mutation.field("createAuthor")
def resolve_create_author(_, info, name):
    author = Author(id=len(authors_db) + 1, name=name)
    authors_db.append(author)
    gravarAuthorDB(name)
    return author

@mutation.field("updateAuthor")
def resolve_update_author(_, info, id, name):
    author= next((a for a in authors_db if a.id == id), None)
    if author:
        author.name = name
        return author
    return None

@mutation.field("deleteAuthor")
def resolve_delete_author(_, info, id):
    global authors_db
    authors_db = [a for a in authors_db if a.id != id]
    return True

@mutation.field("createBook")
def resolve_update_author(_, title , authorIds):
    book = Book (id=len(books_db) + 1, title = title, author_ids=authorIds)
    books_db.append(book)
    gravarBookDB()
    return book

@mutation.field("updateBook")
def resolve_update_author(_,id , title , authorIds):
    book = next((b for b in books_db if b.id == id),None)
    if book:
        book.title = title
        book.author_ids = authorIds
        return book
    return None

@mutation.field("deleteBook")
def resolve_delete_author(_, title , id):
    global books_db
    books_db=[b for b in books_db if b.id != id]

@subscription.source("bookAdicionado")
async def source_book_adicionado(_, info):
    while True:
        await asyncio.sleep(1)
@subscription.field("bookAdicionado")
def resolve_book_adicionado(obj, info):
    return obj["payload"]
