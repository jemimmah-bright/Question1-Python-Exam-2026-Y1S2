from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.student import Student
from app.models.program import Program
from app.models.course import Course
from sqlalchemy.exc import IntegrityError
import re

student_bp = Blueprint("student_bp", __name__)


@student_bp.route("/students", methods=["POST"])
def create_student():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    first_name = data.get("first_name")
    email = data.get("email")
    age = data.get("age")
    program_id = data.get("program_id")
    course_ids = data.get("course_ids", [])

    # Validation
    if not first_name or not str(first_name).strip():
        return jsonify({"error": "first_name is required"}), 400
    if not email or not str(email).strip():
        return jsonify({"error": "email is required"}), 400
    if not program_id:
        return jsonify({"error": "program_id is required"}), 400

    first_name = str(first_name).strip()
    email = str(email).strip().lower()

    # Simple email validation
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return jsonify({"error": "Invalid email address format"}), 400

    # Age validation
    if age is not None:
        try:
            age = int(age)
            if age <= 0:
                return jsonify({"error": "Age must be a positive integer"}), 400
        except ValueError:
            return jsonify({"error": "Age must be an integer"}), 400

    # Check if the program exists
    program = db.session.get(Program, program_id)
    if not program:
        return jsonify({"error": f"Program with ID {program_id} not found"}), 404

    # Check if email is already taken
    existing_student = Student.query.filter_by(email=email).first()
    if existing_student:
        return jsonify({"error": f"Student with email '{email}' already exists"}), 409

    # Resolve course enrollments
    courses_to_enroll = []
    for c_id in course_ids:
        course = db.session.get(Course, c_id)
        if not course:
            return jsonify({"error": f"Course with ID {c_id} not found"}), 404
        if course.program_id != program_id:
            return jsonify({"error": f"Course '{course.name}' (ID {c_id}) does not belong to the selected Program (ID {program_id})"}), 400
        courses_to_enroll.append(course)

    try:
        student = Student(
            first_name=first_name,
            email=email,
            age=age,
            program_id=program_id
        )
        # Enroll in courses
        for course in courses_to_enroll:
            student.courses.append(course)

        db.session.add(student)
        db.session.commit()

        return jsonify({
            "message": "Student created successfully",
            "student": {
                "id": student.id,
                "first_name": student.first_name,
                "email": student.email,
                "age": student.age,
                "program_id": student.program_id,
                "courses": [{"id": c.id, "name": c.name} for c in student.courses]
            }
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity conflict occurred"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@student_bp.route("/students", methods=["GET"])
def get_students():
    students = Student.query.all()

    output = []
    for student in students:
        output.append({
            "id": student.id,
            "first_name": student.first_name,
            "email": student.email,
            "age": student.age,
            "program_id": student.program_id,
            "courses": [{"id": c.id, "name": c.name} for c in student.courses],
            "created_at": student.created_at.isoformat() if student.created_at else None,
            "updated_at": student.updated_at.isoformat() if student.updated_at else None
        })

    return jsonify(output)


@student_bp.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    student = db.get_or_404(Student, id)

    try:
        db.session.delete(student)
        db.session.commit()
        return jsonify({
            "message": "Student deleted successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500