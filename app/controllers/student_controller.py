from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.student import Student

student_bp = Blueprint("student_bp", __name__)


@student_bp.route("/students", methods=["POST"])
def create_student():

    data = request.get_json()

    student = Student(
        first_name=data["first_name"],
        email=data["email"],
        age=data["age"],
        program_id=data["program_id"]
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({
        "message": "Student created successfully"
    }), 201


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
            "program_id": student.program_id
        })

    return jsonify(output)


@student_bp.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):

    student = Student.query.get_or_404(id)

    db.session.delete(student)
    db.session.commit()

    return jsonify({
        "message": "Student deleted successfully"
    })