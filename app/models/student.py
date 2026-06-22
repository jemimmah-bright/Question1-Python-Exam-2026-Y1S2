from app.extensions import db
from datetime import datetime

# Association table for Student <-> Course many-to-many relationship
student_courses = db.Table(
    "student_courses",
    db.Column("student_id", db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    db.Column("created_at", db.DateTime, default=datetime.utcnow)
)


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    age = db.Column(db.Integer)
    program_id = db.Column(
        db.Integer,
        db.ForeignKey("programs.id"),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Many-to-many relationship with Course
    courses = db.relationship(
        "Course",
        secondary=student_courses,
        backref=db.backref("students", lazy="dynamic"),
        lazy="select"
    )