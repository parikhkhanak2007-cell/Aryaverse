import os
from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    render_template,
    jsonify,
    send_from_directory,
    send_file,
    request,
)
from flask_cors import CORS
from sqlalchemy import text

from database import db, State, Region, FolkStory, Translation
from ai_service import (
    translate_story,
    synthesize_speech,
    ask_story_ai,
    check_ai_health,
)


# =========================================================
# APP
# =========================================================

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///aryaverse.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Keep audio files outside the database.
app.config["TTS_DIRECTORY"] = os.path.join(
    app.instance_path,
    "tts",
)

Path(app.instance_path).mkdir(
    parents=True,
    exist_ok=True,
)

Path(app.config["TTS_DIRECTORY"]).mkdir(
    parents=True,
    exist_ok=True,
)


db.init_app(app)
CORS(app)


# =========================================================
# DATABASE SETUP
# =========================================================

with app.app_context():

    db.create_all()

    # -----------------------------------------------------
    # GUJARAT
    # -----------------------------------------------------

    gujarat = State.query.filter_by(
        slug="gujarat"
    ).first()

    if not gujarat:

        gujarat = State(
            name="Gujarat",
            slug="gujarat",
            description=(
                "A land of vibrant festivals, folk traditions, "
                "temples, crafts, food and stories."
            ),
            image="gujarat.png",
        )

        db.session.add(gujarat)
        db.session.commit()


    # -----------------------------------------------------
    # SAMPLE STATES
    # -----------------------------------------------------

    sample_states = [
        {
            "name": "Rajasthan",
            "slug": "rajasthan",
            "description": (
                "A region of forts, folk music, royal traditions, "
                "desert landscapes and colourful culture."
            ),
            "image": "rajasthan.png",
        },
        {
            "name": "Maharashtra",
            "slug": "maharashtra",
            "description": (
                "A cultural landscape shaped by forts, folk traditions, "
                "festivals, literature and diverse communities."
            ),
            "image": "maharashtra.png",
        },
        {
            "name": "West Bengal",
            "slug": "west-bengal",
            "description": (
                "Known for literature, art, festivals, crafts, "
                "music and rich cultural traditions."
            ),
            "image": "west-bengal.png",
        },
    ]

    for data in sample_states:

        existing = State.query.filter_by(
            slug=data["slug"]
        ).first()

        if not existing:

            db.session.add(
                State(
                    name=data["name"],
                    slug=data["slug"],
                    description=data["description"],
                    image=data["image"],
                )
            )

    db.session.commit()


    # -----------------------------------------------------
    # GUJARAT REGIONS
    # -----------------------------------------------------

    regions = [
        {
            "name": "Kutch",
            "slug": "kutch",
            "description": (
                "A culturally rich region known for embroidery, "
                "folk traditions, music, crafts and the Rann."
            ),
            "image": "kutch.png",
        },
        {
            "name": "Saurashtra",
            "slug": "saurashtra",
            "description": (
                "A region of temples, folk traditions, coastal "
                "heritage and distinctive Gujarati culture."
            ),
            "image": "saurashtra.png",
        },
        {
            "name": "North Gujarat",
            "slug": "north-gujarat",
            "description": (
                "Known for traditional communities, heritage sites, "
                "crafts and folk traditions."
            ),
            "image": "north-gujarat.png",
        },
        {
            "name": "South Gujarat",
            "slug": "south-gujarat",
            "description": (
                "A region of forests, tribal traditions, food, "
                "crafts and vibrant cultural practices."
            ),
            "image": "south-gujarat.png",
        },
    ]

    for data in regions:

        existing = Region.query.filter_by(
            state_id=gujarat.id,
            slug=data["slug"],
        ).first()

        if not existing:

            db.session.add(
                Region(
                    state_id=gujarat.id,
                    name=data["name"],
                    slug=data["slug"],
                    description=data["description"],
                    image=data["image"],
                )
            )

    db.session.commit()


    # -----------------------------------------------------
    # KUTCH STORY ONLY IF IT DOES NOT ALREADY EXIST
    # -----------------------------------------------------

    kutch = Region.query.filter_by(
        state_id=gujarat.id,
        slug="kutch",
    ).first()

    if kutch:

        existing_story = FolkStory.query.filter_by(
            slug="living-threads-of-kutch"
        ).first()

        if not existing_story:

            db.session.add(
                FolkStory(
                    region_id=kutch.id,
                    title="The Living Threads of Kutch",
                    slug="living-threads-of-kutch",
                    summary=(
                        "Discover the stories carried through the "
                        "traditional embroidery and textile traditions "
                        "of Kutch."
                    ),
                    story_text=(
                        "Across the villages of Kutch, generations of "
                        "artisans have transformed cloth into a living "
                        "expression of identity, memory and community. "
                        "Traditional embroidery uses colour, patterns "
                        "and symbols that connect everyday life with "
                        "the cultural heritage of the region."
                    ),
                    image="kutch-story.png",
                    audio=None,
                )
            )

        db.session.commit()


    # -----------------------------------------------------
    # COMMUNITY TABLES
    # These are created only when they do not exist.
    # -----------------------------------------------------

    db.session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS story_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                user_name VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

    db.session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS story_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                user_name VARCHAR(100) NOT NULL,
                comment TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

    db.session.commit()


print("Aryaverse database ready.")


# =========================================================
# IMAGE ROUTE
# =========================================================

@app.route("/images/<path:filename>")
def serve_image(filename):

    return send_from_directory(
        "images",
        filename,
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# MAP
# =========================================================

@app.route("/map")
def map_page():
    return render_template("map.html")


# =========================================================
# STATE PAGE
# =========================================================

@app.route("/state/<slug>")
def state_page(slug):

    state = State.query.filter_by(
        slug=slug
    ).first()

    if state is None:

        return (
            f"<h1>State not found</h1>"
            f"<p>No state exists for slug: {slug}</p>"
            f"<p><a href='/map'>Back to map</a></p>",
            404,
        )

    return render_template(
        "state.html",
        state=state,
    )


# =========================================================
# REGION PAGE
# =========================================================

@app.route("/region/<state_slug>/<region_slug>")
def region_page(state_slug, region_slug):

    state = State.query.filter_by(
        slug=state_slug
    ).first_or_404()

    region = Region.query.filter_by(
        state_id=state.id,
        slug=region_slug,
    ).first_or_404()

    return render_template(
        "region.html",
        state=state,
        region=region,
    )


# =========================================================
# STORY PAGE
# =========================================================

@app.route("/story/<int:story_id>")
def story_page(story_id):

    story = FolkStory.query.get_or_404(
        story_id
    )

    return render_template(
        "story.html",
        story=story,
    )


# =========================================================
# API — ALL STATES
# =========================================================

@app.route("/api/states")
def get_states():

    states = State.query.all()

    return jsonify([
        {
            "id": state.id,
            "name": state.name,
            "slug": state.slug,
            "description": state.description,
            "image": state.image,
        }
        for state in states
    ])


# =========================================================
# API — SINGLE STATE
# =========================================================

@app.route("/api/state/<slug>")
def get_state(slug):

    state = State.query.filter_by(
        slug=slug
    ).first_or_404()

    return jsonify({
        "id": state.id,
        "name": state.name,
        "slug": state.slug,
        "description": state.description,
        "image": state.image,
        "regions": [
            {
                "id": region.id,
                "name": region.name,
                "slug": region.slug,
                "description": region.description,
                "image": region.image,
            }
            for region in state.regions
        ],
    })


# =========================================================
# API — REGION
# =========================================================

@app.route("/api/region/<state_slug>/<region_slug>")
def get_region(state_slug, region_slug):

    state = State.query.filter_by(
        slug=state_slug
    ).first_or_404()

    region = Region.query.filter_by(
        state_id=state.id,
        slug=region_slug,
    ).first_or_404()

    return jsonify({
        "id": region.id,
        "name": region.name,
        "slug": region.slug,
        "description": region.description,
        "image": region.image,
        "state": state.name,
        "state_slug": state.slug,
        "stories": [
            {
                "id": story.id,
                "title": story.title,
                "slug": story.slug,
                "summary": story.summary,
                "image": story.image,
            }
            for story in region.stories
        ],
    })


# =========================================================
# API — STORY
# =========================================================

@app.route("/api/story/<int:story_id>")
def get_story(story_id):

    story = FolkStory.query.get_or_404(
        story_id
    )

    return jsonify({
        "id": story.id,
        "title": story.title,
        "summary": story.summary,
        "story_text": story.story_text,
        "image": story.image,
        "audio": story.audio,
        "region": story.region.name,
        "region_slug": story.region.slug,
        "state": story.region.state.name,
        "state_slug": story.region.state.slug,
    })


# =========================================================
# API — AI HEALTH
# =========================================================

@app.route("/api/ai-health")
def ai_health():
    return jsonify(check_ai_health())


# =========================================================
# API — TRANSLATION
# =========================================================

@app.route(
    "/api/story/<int:story_id>/translate",
    methods=["POST"],
)
def story_translate(story_id):

    story = FolkStory.query.get_or_404(
        story_id
    )

    data = request.get_json(
        silent=True
    ) or {}

    language = str(
        data.get("language", "en")
    ).strip().lower()

    try:

        result = translate_story(
            story.story_text,
            language,
        )

        return jsonify({
            "success": True,
            **result,
        })

    except Exception as exc:

        print(
            "STORY TRANSLATION ERROR:",
            repr(exc),
        )

        return jsonify({
            "success": False,
            "error": str(exc),
        }), 500


# =========================================================
# API — TTS
# =========================================================

@app.route(
    "/api/story/<int:story_id>/tts",
    methods=["POST"],
)
def story_tts(story_id):

    story = FolkStory.query.get_or_404(
        story_id
    )

    data = request.get_json(
        silent=True
    ) or {}

    language = str(
        data.get("language", "en")
    ).strip().lower()

    print(
        "TTS REQUEST:",
        story_id,
        language,
    )

    try:

        # -------------------------------------------------
        # Create translated text only when necessary.
        # -------------------------------------------------

        narration_text = story.story_text

        if language != "en":

            translation = translate_story(
                story.story_text,
                language,
            )

            narration_text = translation["text"]


        # -------------------------------------------------
        # Reuse generated audio for this story/language.
        # -------------------------------------------------

        filename = (
            f"story_{story.id}_{language}.mp3"
        )

        audio_path = os.path.join(
            app.config["TTS_DIRECTORY"],
            filename,
        )


        if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000:

            synthesize_speech(
                narration_text,
                language,
                audio_path,
            )


        # -------------------------------------------------
        # Verify the file before returning it.
        # -------------------------------------------------

        if not os.path.exists(audio_path):

            raise RuntimeError(
                "Audio file was not created."
            )


        if os.path.getsize(audio_path) < 1000:

            raise RuntimeError(
                "Generated audio file is empty."
            )


        return send_file(
            audio_path,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name=filename,
            max_age=0,
        )


    except Exception as exc:

        print(
            "STORY TTS ERROR:",
            repr(exc),
        )

        return jsonify({
            "success": False,
            "error": str(exc),
        }), 500


# =========================================================
# API — ASK STORY AI
# =========================================================

@app.route(
    "/api/story/<int:story_id>/ask",
    methods=["POST"],
)
def story_ask(story_id):

    story = FolkStory.query.get_or_404(
        story_id
    )

    data = request.get_json(
        silent=True
    ) or {}

    question = str(
        data.get("question", "")
    ).strip()

    if not question:

        return jsonify({
            "success": False,
            "error": "Please enter a question.",
        }), 400

    try:

        result = ask_story_ai(
            story.story_text,
            question,
        )

        return jsonify({
            "success": True,
            "answer": result["answer"],
        })

    except Exception as exc:

        print(
            "STORY AI ERROR:",
            repr(exc),
        )

        return jsonify({
            "success": False,
            "error": str(exc),
        }), 500


# =========================================================
# API — COMMENTS
# =========================================================

@app.route(
    "/api/story/<int:story_id>/comments",
    methods=["GET", "POST"],
)
def story_comments(story_id):

    FolkStory.query.get_or_404(
        story_id
    )

    if request.method == "GET":

        rows = db.session.execute(
            text(
                """
                SELECT id, user_name, comment, created_at
                FROM story_comments
                WHERE story_id = :story_id
                ORDER BY id DESC
                """
            ),
            {"story_id": story_id},
        ).mappings().all()

        return jsonify({
            "comments": [dict(row) for row in rows]
        })


    data = request.get_json(
        silent=True
    ) or {}

    user_name = str(
        data.get("user_name", "")
    ).strip()

    comment = str(
        data.get("comment", "")
    ).strip()

    if not user_name:

        return jsonify({
            "success": False,
            "error": "Name is required.",
        }), 400

    if not comment:

        return jsonify({
            "success": False,
            "error": "Comment is required.",
        }), 400

    db.session.execute(
        text(
            """
            INSERT INTO story_comments
                (story_id, user_name, comment, created_at)
            VALUES
                (:story_id, :user_name, :comment, :created_at)
            """
        ),
        {
            "story_id": story_id,
            "user_name": user_name[:100],
            "comment": comment[:1000],
            "created_at": datetime.utcnow(),
        },
    )

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Comment posted.",
    }), 201


# =========================================================
# API — LIKE
# =========================================================

@app.route(
    "/api/story/<int:story_id>/like",
    methods=["POST"],
)
def story_like(story_id):

    FolkStory.query.get_or_404(
        story_id
    )

    data = request.get_json(
        silent=True
    ) or {}

    user_name = str(
        data.get("user_name", "Anonymous")
    ).strip() or "Anonymous"

    existing = db.session.execute(
        text(
            """
            SELECT id
            FROM story_likes
            WHERE story_id = :story_id
              AND user_name = :user_name
            LIMIT 1
            """
        ),
        {
            "story_id": story_id,
            "user_name": user_name[:100],
        },
    ).first()

    if existing:

        db.session.execute(
            text(
                "DELETE FROM story_likes WHERE id = :id"
            ),
            {"id": existing[0]},
        )

        liked = False

    else:

        db.session.execute(
            text(
                """
                INSERT INTO story_likes
                    (story_id, user_name, created_at)
                VALUES
                    (:story_id, :user_name, :created_at)
                """
            ),
            {
                "story_id": story_id,
                "user_name": user_name[:100],
                "created_at": datetime.utcnow(),
            },
        )

        liked = True

    db.session.commit()

    count = db.session.execute(
        text(
            "SELECT COUNT(*) FROM story_likes WHERE story_id = :story_id"
        ),
        {"story_id": story_id},
    ).scalar_one()

    return jsonify({
        "success": True,
        "liked": liked,
        "count": count,
    })


# =========================================================
# API — BASIC HEALTH
# =========================================================

@app.route("/api/health")
def health():

    return jsonify({
        "status": "ok",
        "service": "Aryaverse",
    })


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
