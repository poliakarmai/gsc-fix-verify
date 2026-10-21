import csv
import io

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response

from models.book import get_all_books, search_books, get_all_categories, add_book

books_bp = Blueprint("books", __name__, url_prefix="/books")


@books_bp.route("/")
def list_books():
    # using GET params so the filtered URL is bookmarkable (e.g. /books/?category=Science)
    query    = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    books      = search_books(query, category)
    categories = get_all_categories()

    return render_template(
        "books.html",
        books=books,
        categories=categories,
        current_query=query,
        current_category=category,
    )


@books_bp.route("/add", methods=["GET", "POST"])
def add_book_view():
    if request.method == "POST":
        title      = request.form.get("title", "").strip()
        author     = request.form.get("author", "").strip()
        isbn       = request.form.get("isbn", "").strip() or None
        category   = request.form.get("category", "").strip() or None
        copies_raw = request.form.get("total_copies", "").strip()

        if not title or not author:
            flash("Title and Author are required.", "error")
            return render_template("add_book.html")

        try:
            total_copies = int(copies_raw)
            if total_copies < 1:
                raise ValueError
        except ValueError:
            flash("Total copies must be a whole number ≥ 1.", "error")
            return render_template("add_book.html")

        try:
            add_book(title, author, isbn, category, total_copies)
            flash(f"'{title}' added successfully.", "success")
            return redirect(url_for("books.list_books"))
        except Exception as e:
            # most likely a duplicate ISBN hitting the UNIQUE constraint
            flash(f"Could not add book: {e}", "error")
            return render_template("add_book.html")

    return render_template("add_book.html")


@books_bp.route("/export.csv")
def export_books():
    """Download the current book list as CSV (respects the active filter)."""
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    books = search_books(query, category)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Title", "Author", "ISBN", "Category", "Total", "Available"])
    for b in books:
        writer.writerow([b["title"], b["author"], b["isbn"] or "",
                         b["category"] or "", b["total_copies"], b["available_copies"]])

    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=books.csv"},
    )



@books_bp.route("/export.csv")
def export_books():
    """CSV export of the filtered book list."""
    import csv, io
    from flask import Response
    books = search_books(request.args.get("q","").strip(), request.args.get("category","").strip())
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Title","Author"])
    for b in books: w.writerow([b["title"], b["author"]])
    return Response(buf.getvalue(), mimetype="text/csv")
