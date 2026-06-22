import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def request_api(path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    payload = json.dumps(data).encode("utf-8") if data is not None else None
    
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as res:
            status = res.status
            body = json.loads(res.read().decode("utf-8"))
            return status, body
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = e.reason
        return status, body
    except Exception as e:
        return 500, str(e)

def print_result(test_name, expected_status, actual_status, body):
    if actual_status == expected_status:
        print(f"[PASS] {test_name}: Status {actual_status}")
    else:
        print(f"[FAIL] {test_name}: Expected {expected_status}, Got {actual_status}")
        print(f"   Response: {body}")
        sys.exit(1)

def run_tests():
    print("Starting Student Management System API Tests...")
    print("-" * 50)
    
    # 1. POST /programs (Success)
    status, body = request_api("/programs", "POST", {
        "name": "Bachelor of Science in Software Engineering",
        "code": "BSSE"
    })
    print_result("1. Create Program BSSE", 201, status, body)
    program_id = body["program"]["id"]
    
    # 2. POST /programs (Duplicate Code - should fail with 409)
    status, body = request_api("/programs", "POST", {
        "name": "Another Program",
        "code": "BSSE"
    })
    print_result("2. Create Duplicate Program", 409, status, body)
    
    # 3. POST /programs (Missing Field - should fail with 400)
    status, body = request_api("/programs", "POST", {
        "name": "No Code Program"
    })
    print_result("3. Create Program Missing Code", 400, status, body)
    
    # 4. POST /courses (Success)
    status, body = request_api("/courses", "POST", {
        "name": "Web Application Development",
        "program_id": program_id
    })
    print_result("4. Create Course", 201, status, body)
    course_id = body["course"]["id"]
    
    # 5. POST /courses (Non-existent Program - should fail with 404)
    status, body = request_api("/courses", "POST", {
        "name": "Advanced Python",
        "program_id": 999
    })
    print_result("5. Create Course with invalid program_id", 404, status, body)

    # 6. POST /students (Success with enrollment)
    status, body = request_api("/students", "POST", {
        "first_name": "Mary Nabakka",
        "email": "mary.nabakka@witi.ac.ug",
        "age": 21,
        "program_id": program_id,
        "course_ids": [course_id]
    })
    print_result("6. Create Student with course enrollment", 201, status, body)
    student_id = body["student"]["id"]
    
    # 7. POST /students (Duplicate Email - should fail with 409)
    status, body = request_api("/students", "POST", {
        "first_name": "Mary Copy",
        "email": "mary.nabakka@witi.ac.ug",
        "age": 22,
        "program_id": program_id
    })
    print_result("7. Create Student with duplicate email", 409, status, body)

    # 8. POST /students (Invalid Email format - should fail with 400)
    status, body = request_api("/students", "POST", {
        "first_name": "Winnie Among",
        "email": "winnieamong-witi.ac.ug",
        "age": 20,
        "program_id": program_id
    })
    print_result("8. Create Student with invalid email format", 400, status, body)

    # 9. GET /students (Success)
    status, body = request_api("/students", "GET")
    print_result("9. Get All Students", 200, status, body)
    assert len(body) > 0, "No students returned"
    print(f"   Returned {len(body)} student(s).")
    
    # 10. PUT /programs/<id> (Success)
    status, body = request_api(f"/programs/{program_id}", "PUT", {
        "name": "BS in Software Engineering (WITI)"
    })
    print_result("10. Update Program Name", 200, status, body)
    
    # 11. DELETE /students/<id> (Success)
    status, body = request_api(f"/students/{student_id}", "DELETE")
    print_result("11. Delete Student", 200, status, body)
    
    # 12. GET /students (Verify delete)
    status, body = request_api("/students", "GET")
    print_result("12. Get Students (empty list check)", 200, status, body)
    matching_students = [s for s in body if s["id"] == student_id]
    if len(matching_students) == 0:
        print("[PASS] 13. Verify Student deletion")
    else:
        print("[FAIL] 13. Verify Student deletion")
        sys.exit(1)
        
    print("-" * 50)
    print("All API validation tests PASSED successfully!")

if __name__ == "__main__":
    run_tests()
