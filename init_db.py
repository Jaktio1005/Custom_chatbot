from database import db
import json
import os

# Sample course data
sample_courses = [
    {
        "title": "Python Programming Course",
        "description": "Learn Python programming from basics to advanced concepts. This comprehensive course covers variables, data structures, functions, OOP, and more.",
        "category": "technical"
    },
    {
        "title": "Web Development Bootcamp",
        "description": "Master full-stack web development with HTML, CSS, JavaScript, React, Node.js, and MongoDB. Build real-world projects and deploy them.",
        "category": "technical"
    },
    {
        "title": "Data Science Fundamentals",
        "description": "Explore data science concepts including data analysis, visualization, machine learning, and statistical analysis using Python libraries.",
        "category": "technical"
    },
    {
        "title": "Artificial Intelligence Basics",
        "description": "Introduction to AI concepts, machine learning algorithms, neural networks, and practical applications in various industries.",
        "category": "technical"
    },
    {
        "title": "Cloud Computing Essentials",
        "description": "Learn cloud computing fundamentals with AWS, Azure, and Google Cloud. Understand cloud architecture, deployment, and best practices.",
        "category": "technical"
    }
]

def init_database():
    """Initialize the database with sample courses."""
    # Clear existing courses
    if os.path.exists(db.courses_file):
        with open(db.courses_file, 'w') as f:
            json.dump({"courses": []}, f, indent=2)
    
    # Insert sample courses
    for course in sample_courses:
        db.save_course(
            title=course["title"],
            description=course["description"],
            category=course["category"]
        )
    print("Database initialized with sample courses!")

if __name__ == "__main__":
    init_database() 