import json
from datetime import datetime
import os
from typing import List, Dict, Optional

class Database:
    def __init__(self):
        self.data_dir = "data"
        self.chats_file = os.path.join(self.data_dir, "chats.json")
        self.courses_file = os.path.join(self.data_dir, "courses.json")
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Initialize files if they don't exist
        self._init_file(self.chats_file, {"chats": []})
        self._init_file(self.courses_file, {"courses": []})

    def _init_file(self, file_path: str, default_data: Dict):
        """Initialize a JSON file if it doesn't exist."""
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump(default_data, f, indent=2)

    def _load_data(self, file_path: str) -> Dict:
        """Load data from a JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)

    def _save_data(self, file_path: str, data: Dict):
        """Save data to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def save_chat(self, user_question: str, bot_answer: str, sources: Optional[List] = None) -> None:
        """Save chat interaction to file."""
        data = self._load_data(self.chats_file)
        chat_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_question": user_question,
            "bot_answer": bot_answer,
            "sources": sources or []
        }
        data["chats"].append(chat_record)
        self._save_data(self.chats_file, data)

    def get_chat_history(self, limit: int = 50) -> List[Dict]:
        """Retrieve chat history."""
        data = self._load_data(self.chats_file)
        return sorted(data["chats"], key=lambda x: x["timestamp"], reverse=True)[:limit]

    def save_course(self, title: str, description: str, category: str = "technical") -> None:
        """Save course information to file."""
        data = self._load_data(self.courses_file)
        course_record = {
            "title": title,
            "description": description,
            "category": category,
            "created_at": datetime.utcnow().isoformat()
        }
        # Update if exists, otherwise append
        course_exists = False
        for i, course in enumerate(data["courses"]):
            if course["title"] == title:
                data["courses"][i] = course_record
                course_exists = True
                break
        
        if not course_exists:
            data["courses"].append(course_record)
        
        self._save_data(self.courses_file, data)

    def get_courses(self, category: Optional[str] = None) -> List[Dict]:
        """Retrieve courses with optional category filter."""
        data = self._load_data(self.courses_file)
        if category:
            return [course for course in data["courses"] if course["category"] == category]
        return data["courses"]

    def get_course_by_title(self, title: str) -> Optional[Dict]:
        """Retrieve a specific course by title."""
        data = self._load_data(self.courses_file)
        for course in data["courses"]:
            if course["title"] == title:
                return course
        return None

    def update_course(self, title: str, updates: Dict) -> bool:
        """Update course information."""
        data = self._load_data(self.courses_file)
        for i, course in enumerate(data["courses"]):
            if course["title"] == title:
                data["courses"][i].update(updates)
                self._save_data(self.courses_file, data)
                return True
        return False

    def delete_course(self, title: str) -> bool:
        """Delete a course."""
        data = self._load_data(self.courses_file)
        initial_length = len(data["courses"])
        data["courses"] = [course for course in data["courses"] if course["title"] != title]
        if len(data["courses"]) < initial_length:
            self._save_data(self.courses_file, data)
            return True
        return False

# Initialize database
db = Database() 