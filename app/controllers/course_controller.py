from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.course import Course
from app.models.program import Program
from sqlalchemy.exc import IntegrityError

course_bp = Blueprint("course_bp", __name__)


@course_bp.route("/courses", methods=["POST"])
def create_course():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    name = data.get("name")
    program_id = data.get("program_id")

    if not name or not str(name).strip():
        return jsonify({"error": "Course name is required"}), 400
    if not program_id:
        return jsonify({"error": "program_id is required"}), 400

    name = str(name).strip()

    # Check if the program exists
    program = db.session.get(Program, program_id)
    if not program:
        return jsonify({"error": f"Program with ID {program_id} not found"}), 404

    # Prevent duplicate courses within the same program
    existing_course = Course.query.filter_by(name=name, program_id=program_id).first()
    if existing_course:
        return jsonify({"error": f"Course '{name}' already exists in this program"}), 409

    try:
        course = Course(name=name, program_id=program_id)
        db.session.add(course)
        db.session.commit()

        return jsonify({
            "message": "Course created successfully",
            "course": {
                "id": course.id,
                "name": course.name,
                "program_id": course.program_id
            }
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity conflict occurred"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500