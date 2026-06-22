from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.program import Program
from sqlalchemy.exc import IntegrityError

program_bp = Blueprint("program_bp", __name__)


@program_bp.route("/programs", methods=["POST"])
def create_program():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    name = data.get("name")
    code = data.get("code")

    if not name or not str(name).strip():
        return jsonify({"error": "Program name is required"}), 400
    if not code or not str(code).strip():
        return jsonify({"error": "Program code is required"}), 400

    name = str(name).strip()
    code = str(code).strip().upper()

    # Check if a program with the same code already exists
    existing_program = Program.query.filter_by(code=code).first()
    if existing_program:
        return jsonify({"error": f"Program with code '{code}' already exists"}), 409

    try:
        program = Program(name=name, code=code)
        db.session.add(program)
        db.session.commit()

        return jsonify({
            "message": "Program created successfully",
            "program": {
                "id": program.id,
                "name": program.name,
                "code": program.code
            }
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity conflict occurred"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@program_bp.route("/programs/<int:id>", methods=["PUT"])
def update_program(id):
    program = db.get_or_404(Program, id)

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    name = data.get("name")
    code = data.get("code")

    if "name" in data:
        if not name or not str(name).strip():
            return jsonify({"error": "Program name cannot be empty"}), 400
        program.name = str(name).strip()

    if "code" in data:
        if not code or not str(code).strip():
            return jsonify({"error": "Program code cannot be empty"}), 400
        new_code = str(code).strip().upper()

        if new_code != program.code:
            # Check for conflict
            existing_program = Program.query.filter_by(code=new_code).first()
            if existing_program:
                return jsonify({"error": f"Program with code '{new_code}' already exists"}), 409
            program.code = new_code

    try:
        db.session.commit()
        return jsonify({
            "message": "Program updated successfully",
            "program": {
                "id": program.id,
                "name": program.name,
                "code": program.code
            }
        }), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity conflict occurred"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500