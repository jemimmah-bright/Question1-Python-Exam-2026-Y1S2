from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.program import Program

program_bp = Blueprint("program_bp", __name__)


@program_bp.route("/programs", methods=["POST"])
def create_program():

    data = request.get_json()

    program = Program(
        name=data["name"],
        code=data["code"]
    )

    db.session.add(program)
    db.session.commit()

    return jsonify({
        "message": "Program created successfully"
    }), 201


@program_bp.route("/programs/<int:id>", methods=["PUT"])
def update_program(id):

    program = Program.query.get_or_404(id)

    data = request.get_json()

    program.name = data["name"]
    program.code = data["code"]

    db.session.commit()

    return jsonify({
        "message": "Program updated successfully"
    })