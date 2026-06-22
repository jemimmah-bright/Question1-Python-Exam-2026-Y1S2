from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.course import Course

course_bp = Blueprint("course_bp", __name__)


@course_bp.route("/courses", methods=["POST"])
def create_course():

    data = request.get_json()

    course = Course(
        name=data["name"],
        program_id=data["program_id"]
    )

    db.session.add(course)
    db.session.commit()

    return jsonify({
        "message": "Course created successfully"
    }), 201