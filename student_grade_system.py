"""
Student Grade Management System
================================
This program demonstrates:
1. Dictionary - to store student information
2. For loops - to iterate through students and grades
3. Conditions - to evaluate pass/fail and letter grades

Real Use Case: A teacher wants to manage student grades and 
automatically calculate their average and letter grade.
"""

# Dictionary to store student information
# Each student has: name, grades (list of scores), and subjects
students = {
    "student_001": {
        "name": "Alice Johnson",
        "grades": [85, 92, 78, 90],
        "subjects": ["Math", "Science", "English", "History"]
    },
    "student_002": {
        "name": "Bob Smith",
        "grades": [72, 68, 75, 70],
        "subjects": ["Math", "Science", "English", "History"]
    },
    "student_003": {
        "name": "Charlie Brown",
        "grades": [95, 88, 92, 94],
        "subjects": ["Math", "Science", "English", "History"]
    },
    "student_004": {
        "name": "Diana Prince",
        "grades": [55, 62, 58, 65],
        "subjects": ["Math", "Science", "English", "History"]
    }
}


def calculate_average(grades):
    """Calculate the average of a list of grades"""
    if not grades:  # Handle empty list
        return 0
    return sum(grades) / len(grades)


def get_letter_grade(average):
    """
    Determine letter grade based on average score
    Using conditions (if/elif/else)
    """
    if average >= 90:
        return "A"
    elif average >= 80:
        return "B"
    elif average >= 70:
        return "C"
    elif average >= 60:
        return "D"
    else:
        return "F"


def get_status(average):
    """Determine if student passed or failed using conditions"""
    if average >= 60:
        return "PASSED"
    else:
        return "FAILED"


# Main program execution
print("=" * 60)
print("STUDENT GRADE MANAGEMENT SYSTEM")
print("=" * 60)
print()

# Store student results for later use in summary
student_results = []

# For loop to iterate through all students in the dictionary
for student_id, student_info in students.items():
    # Extract student information from dictionary
    name = student_info["name"]
    grades = student_info["grades"]
    subjects = student_info["subjects"]
    
    # Calculate average
    average = calculate_average(grades)
    
    # Get letter grade using conditions
    letter_grade = get_letter_grade(average)
    
    # Get pass/fail status using conditions
    status = get_status(average)
    
    # Store results for summary statistics
    student_results.append({"name": name, "average": average, "status": status})
    
    # Display student report
    print(f"Student ID: {student_id}")
    print(f"Name: {name}")
    print(f"Subjects and Grades:")
    
    # For loop to iterate through subjects and corresponding grades
    # Using zip() for better Pythonic style
    for subject, grade in zip(subjects, grades):
        # Condition to highlight low grades
        if grade < 60:
            print(f"  - {subject}: {grade} ⚠️ (Below passing)")
        else:
            print(f"  - {subject}: {grade}")
    
    print(f"Average Grade: {average:.2f}")
    print(f"Letter Grade: {letter_grade}")
    print(f"Status: {status}")
    
    # Condition to provide encouragement or congratulations
    if status == "PASSED":
        if average >= 90:
            print("🌟 Excellent work! Keep it up!")
        elif average >= 80:
            print("👍 Great job!")
        else:
            print("✓ Good effort, keep improving!")
    else:
        print("⚠️ Need to study harder. Don't give up!")
    
    print("-" * 60)
    print()

# Summary statistics using stored results
print("=" * 60)
print("SUMMARY STATISTICS")
print("=" * 60)

total_students = len(student_results)
passed_students = 0
failed_students = 0

# For loop to count passed and failed students using stored results
for result in student_results:
    # Condition to count passed/failed students
    if result["status"] == "PASSED":
        passed_students += 1
    else:
        failed_students += 1

print(f"Total Students: {total_students}")
print(f"Passed: {passed_students}")
print(f"Failed: {failed_students}")
print(f"Pass Rate: {(passed_students / total_students) * 100:.1f}%")
print("=" * 60)
