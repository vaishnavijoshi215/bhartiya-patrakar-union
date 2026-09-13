from flask import Flask, render_template, request, redirect, url_for, session
from database import get_db_connection, init_db
from werkzeug.utils import secure_filename

import os
import time
import re


app = Flask(__name__)

# =========================================================
# APP SETTINGS
# =========================================================

app.secret_key = "bpu-local-secret-key"

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def valid_email(email):

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.match(pattern, email) is not None


def valid_phone(phone):

    return phone.isdigit() and len(phone) == 10


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    conn = get_db_connection()

    latest_news = conn.execute("""
        SELECT *
        FROM news
        ORDER BY id DESC
        LIMIT 3
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        latest_news=latest_news
    )


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():

    return render_template("about.html")


# =========================================================
# NEWS
# =========================================================

@app.route("/news")
def news():

    conn = get_db_connection()

    news_list = conn.execute("""
        SELECT *
        FROM news
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "news.html",
        news=news_list
    )


# =========================================================
# NEWS DETAIL
# =========================================================

@app.route("/news/<int:news_id>")
def news_detail(news_id):

    conn = get_db_connection()

    item = conn.execute("""
        SELECT *
        FROM news
        WHERE id = ?
    """, (news_id,)).fetchone()

    conn.close()

    if item is None:
        return "News not found", 404

    return render_template(
        "news_detail.html",
        news=item
    )


# =========================================================
# EVENTS
# =========================================================

@app.route("/events")
def events():

    conn = get_db_connection()

    events_list = conn.execute("""
        SELECT *
        FROM events
        ORDER BY event_date ASC
    """).fetchall()

    conn.close()

    return render_template(
        "events.html",
        events=events_list
    )


# =========================================================
# GALLERY
# =========================================================

@app.route("/gallery")
def gallery():

    conn = get_db_connection()

    gallery_list = conn.execute("""
        SELECT *
        FROM gallery
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "gallery.html",
        gallery=gallery_list
    )


# =========================================================
# MEMBERSHIP
# =========================================================

@app.route("/membership", methods=["GET", "POST"])
def membership():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        city = request.form.get("city", "").strip()
        profession = request.form.get("profession", "").strip()
        message = request.form.get("message", "").strip()


        # -------------------------
        # SERVER-SIDE VALIDATION
        # -------------------------

        if not name or not email or not phone or not city:

            return render_template(
                "membership.html",
                error="Please fill all required fields."
            )


        if not valid_email(email):

            return render_template(
                "membership.html",
                error="Please enter a valid email address."
            )


        if not valid_phone(phone):

            return render_template(
                "membership.html",
                error="Phone number must contain exactly 10 digits."
            )


        # -------------------------
        # SAVE TO DATABASE
        # -------------------------

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO memberships
            (
                name,
                email,
                phone,
                city,
                profession,
                message
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            phone,
            city,
            profession,
            message
        ))

        conn.commit()
        conn.close()


        return render_template(
            "success.html",
            title="Membership Application Submitted",
            message="Thank you! Your membership application has been submitted successfully."
        )


    return render_template("membership.html")


# =========================================================
# CONTACT
# =========================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()


        # -------------------------
        # SERVER-SIDE VALIDATION
        # -------------------------

        if not name or not email or not subject or not message:

            return render_template(
                "contact.html",
                error="Please fill all required fields."
            )


        if not valid_email(email):

            return render_template(
                "contact.html",
                error="Please enter a valid email address."
            )


        # -------------------------
        # SAVE MESSAGE
        # -------------------------

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO contact_messages
            (
                name,
                email,
                subject,
                message
            )
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            subject,
            message
        ))

        conn.commit()
        conn.close()


        return render_template(
            "success.html",
            title="Message Sent Successfully",
            message="Thank you for contacting Bhartiya Patrakar Union. We will get back to you soon."
        )


    return render_template("contact.html")


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()


        # LOCAL TESTING CREDENTIALS
        ADMIN_USERNAME = "admin"
        ADMIN_PASSWORD = "BPU@12345"


        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin_dashboard")
            )


        return render_template(
            "admin/login.html",
            error="Invalid username or password."
        )


    return render_template("admin/login.html")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin_dashboard():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    conn = get_db_connection()


    memberships = conn.execute("""
        SELECT *
        FROM memberships
        ORDER BY id DESC
    """).fetchall()


    news_list = conn.execute("""
        SELECT *
        FROM news
        ORDER BY id DESC
    """).fetchall()


    gallery_list = conn.execute("""
        SELECT *
        FROM gallery
        ORDER BY id DESC
    """).fetchall()


    contact_messages = conn.execute("""
        SELECT *
        FROM contact_messages
        ORDER BY id DESC
    """).fetchall()


    events_list = conn.execute("""
        SELECT *
        FROM events
        ORDER BY event_date ASC
    """).fetchall()


    conn.close()


    return render_template(
        "admin/dashboard.html",
        memberships=memberships,
        news=news_list,
        gallery=gallery_list,
        contact_messages=contact_messages,
        events=events_list
    )


# =========================================================
# ADMIN - ADD NEWS
# =========================================================

@app.route("/admin/news/add", methods=["GET", "POST"])
def add_news():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    if request.method == "POST":

        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        content = request.form.get("content", "").strip()

        file = request.files.get("image")

        image_name = None


        if not title or not category or not content:

            return render_template(
                "admin/add_news.html",
                error="Please fill all required fields."
            )


        # -------------------------
        # IMAGE UPLOAD
        # -------------------------

        if file and file.filename:

            if not allowed_file(file.filename):

                return render_template(
                    "admin/add_news.html",
                    error="Invalid image format."
                )


            original_name = secure_filename(
                file.filename
            )


            extension = original_name.rsplit(
                ".",
                1
            )[1].lower()


            image_name = (
                str(int(time.time()))
                + "_"
                + original_name
            )


            file.save(
                os.path.join(
                    UPLOAD_FOLDER,
                    image_name
                )
            )


        # -------------------------
        # DATABASE
        # -------------------------

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO news
            (
                title,
                category,
                content,
                image
            )
            VALUES (?, ?, ?, ?)
        """, (
            title,
            category,
            content,
            image_name
        ))

        conn.commit()
        conn.close()


        return redirect(
            url_for("admin_dashboard")
        )


    return render_template(
        "admin/add_news.html"
    )


# =========================================================
# ADMIN - EDIT NEWS
# =========================================================

@app.route(
    "/admin/news/edit/<int:news_id>",
    methods=["GET", "POST"]
)
def edit_news(news_id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    conn = get_db_connection()


    news_item = conn.execute("""
        SELECT *
        FROM news
        WHERE id = ?
    """, (news_id,)).fetchone()


    if news_item is None:

        conn.close()

        return "News not found", 404


    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        ).strip()


        file = request.files.get("image")

        image_name = news_item["image"]


        if not title or not category or not content:

            conn.close()

            return render_template(
                "admin/edit_news.html",
                news=news_item,
                error="Please fill all required fields."
            )


        # -------------------------
        # NEW IMAGE
        # -------------------------

        if file and file.filename:

            if not allowed_file(file.filename):

                conn.close()

                return render_template(
                    "admin/edit_news.html",
                    news=news_item,
                    error="Invalid image format."
                )


            original_name = secure_filename(
                file.filename
            )


            extension = original_name.rsplit(
                ".",
                1
            )[1].lower()


            new_image_name = (
                str(int(time.time()))
                + "_"
                + original_name
            )


            file.save(
                os.path.join(
                    UPLOAD_FOLDER,
                    new_image_name
                )
            )


            # Delete old image

            if image_name:

                old_path = os.path.join(
                    UPLOAD_FOLDER,
                    image_name
                )

                if os.path.exists(old_path):

                    os.remove(old_path)


            image_name = new_image_name


        # -------------------------
        # UPDATE
        # -------------------------

        conn.execute("""
            UPDATE news
            SET
                title = ?,
                category = ?,
                content = ?,
                image = ?
            WHERE id = ?
        """, (
            title,
            category,
            content,
            image_name,
            news_id
        ))


        conn.commit()
        conn.close()


        return redirect(
            url_for("admin_dashboard")
        )


    conn.close()


    return render_template(
        "admin/edit_news.html",
        news=news_item
    )


# =========================================================
# ADMIN - DELETE NEWS
# =========================================================

@app.route(
    "/admin/news/delete/<int:news_id>"
)
def delete_news(news_id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    conn = get_db_connection()


    news_item = conn.execute("""
        SELECT image
        FROM news
        WHERE id = ?
    """, (news_id,)).fetchone()


    if news_item:

        image_name = news_item["image"]


        if image_name:

            image_path = os.path.join(
                UPLOAD_FOLDER,
                image_name
            )


            if os.path.exists(image_path):

                os.remove(image_path)


        conn.execute("""
            DELETE FROM news
            WHERE id = ?
        """, (news_id,))


        conn.commit()


    conn.close()


    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADMIN - ADD GALLERY
# =========================================================

@app.route(
    "/admin/gallery/add",
    methods=["GET", "POST"]
)
def add_gallery():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        file = request.files.get("image")


        if not title or not file or not file.filename:

            return render_template(
                "admin/add_gallery.html",
                error="Please enter title and select an image."
            )


        if not allowed_file(file.filename):

            return render_template(
                "admin/add_gallery.html",
                error="Invalid image format."
            )


        original_name = secure_filename(
            file.filename
        )


        image_name = (
            str(int(time.time()))
            + "_"
            + original_name
        )


        file.save(
            os.path.join(
                UPLOAD_FOLDER,
                image_name
            )
        )


        conn = get_db_connection()


        conn.execute("""
            INSERT INTO gallery
            (
                title,
                image
            )
            VALUES (?, ?)
        """, (
            title,
            image_name
        ))


        conn.commit()
        conn.close()


        return redirect(
            url_for("admin_dashboard")
        )


    return render_template(
        "admin/add_gallery.html"
    )


# =========================================================
# ADMIN - DELETE GALLERY
# =========================================================

@app.route(
    "/admin/gallery/delete/<int:gallery_id>"
)
def delete_gallery(gallery_id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    conn = get_db_connection()


    item = conn.execute("""
        SELECT image
        FROM gallery
        WHERE id = ?
    """, (gallery_id,)).fetchone()


    if item:

        image_name = item["image"]


        if image_name:

            image_path = os.path.join(
                UPLOAD_FOLDER,
                image_name
            )


            if os.path.exists(image_path):

                os.remove(image_path)


        conn.execute("""
            DELETE FROM gallery
            WHERE id = ?
        """, (gallery_id,))


        conn.commit()


    conn.close()


    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADMIN - ADD EVENT
# =========================================================

@app.route(
    "/admin/events/add",
    methods=["GET", "POST"]
)
def add_event():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        event_date = request.form.get(
            "event_date",
            ""
        ).strip()

        venue = request.form.get(
            "venue",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()


        if (
            not title
            or not event_date
            or not venue
            or not description
        ):

            return render_template(
                "admin/add_event.html",
                error="Please fill all required fields."
            )


        conn = get_db_connection()


        conn.execute("""
            INSERT INTO events
            (
                title,
                event_date,
                venue,
                description
            )
            VALUES (?, ?, ?, ?)
        """, (
            title,
            event_date,
            venue,
            description
        ))


        conn.commit()
        conn.close()


        return redirect(
            url_for("admin_dashboard")
        )


    return render_template(
        "admin/add_event.html"
    )


# =========================================================
# ADMIN - EDIT EVENT
# =========================================================

@app.route(
    "/admin/events/edit/<int:event_id>",
    methods=["GET", "POST"]
)
def edit_event(event_id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    conn = get_db_connection()


    event = conn.execute("""
        SELECT *
        FROM events
        WHERE id = ?
    """, (event_id,)).fetchone()


    if event is None:

        conn.close()

        return "Event not found", 404


    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        event_date = request.form.get(
            "event_date",
            ""
        ).strip()

        venue = request.form.get(
            "venue",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()


        if (
            not title
            or not event_date
            or not venue
            or not description
        ):

            conn.close()

            return render_template(
                "admin/edit_event.html",
                event=event,
                error="Please fill all required fields."
            )


        conn.execute("""
            UPDATE events
            SET
                title = ?,
                event_date = ?,
                venue = ?,
                description = ?
            WHERE id = ?
        """, (
            title,
            event_date,
            venue,
            description,
            event_id
        ))


        conn.commit()
        conn.close()


        return redirect(
            url_for("admin_dashboard")
        )


    conn.close()


    return render_template(
        "admin/edit_event.html",
        event=event
    )


# =========================================================
# ADMIN - DELETE EVENT
# =========================================================

@app.route(
    "/admin/events/delete/<int:event_id>"
)
def delete_event(event_id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    conn = get_db_connection()


    conn.execute("""
        DELETE FROM events
        WHERE id = ?
    """, (event_id,))


    conn.commit()
    conn.close()


    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# SEO - ROBOTS.TXT
# =========================================================

@app.route("/robots.txt")
def robots():

    return app.send_static_file(
        "robots.txt"
    )


# =========================================================
# SEO - SITEMAP.XML
# =========================================================

@app.route("/sitemap.xml")
def sitemap():

    return app.send_static_file(
        "sitemap.xml"
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )