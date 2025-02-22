import json
import os
from datetime import datetime, timedelta

class UserStats:
    def __init__(self, filename="user_stats.json"):
        self.filename = filename
        self.stats = self._load_stats()

    def _load_stats(self):
        """Load stats from file or create new if file doesn't exist or is corrupted"""
        default_stats = self._create_default_stats()

        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    loaded_stats = json.load(f)

                # Migrate old format to new format
                if isinstance(loaded_stats.get("total_users"), list):
                    migrated_stats = self._migrate_old_format(loaded_stats)
                    self._save_stats(migrated_stats)
                    return migrated_stats

                # Ensure the loaded stats have the required structure
                if not isinstance(loaded_stats, dict):
                    return default_stats
                if "users" not in loaded_stats:
                    loaded_stats["users"] = {}
                if "total_quizzes" not in loaded_stats:
                    loaded_stats["total_quizzes"] = 0
                return loaded_stats
            except Exception as e:
                print(f"Error loading stats: {e}")
                return default_stats
        return default_stats

    def _migrate_old_format(self, old_stats):
        """Migrate from old stats format to new format"""
        new_stats = self._create_default_stats()
        current_time = datetime.now().isoformat()

        # Convert user IDs to strings and create user entries
        for user_id in old_stats.get("total_users", []):
            str_user_id = str(user_id)
            quiz_count = old_stats.get("quiz_count", {}).get(str_user_id, 0)

            new_stats["users"][str_user_id] = {
                "first_seen": current_time,
                "last_active": current_time,
                "username": None,
                "quizzes_created": quiz_count
            }

            # Update total quizzes count
            new_stats["total_quizzes"] += quiz_count

        return new_stats

    def _create_default_stats(self):
        """Create default stats structure"""
        return {
            "users": {},
            "total_quizzes": 0
        }

    def _save_stats(self, stats_to_save=None):
        """Save stats to file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(stats_to_save or self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def record_user_activity(self, user_id, username=None):
        """Record user activity with timestamp"""
        str_user_id = str(user_id)
        current_time = datetime.now().isoformat()

        if "users" not in self.stats:
            self.stats["users"] = {}

        if str_user_id not in self.stats["users"]:
            self.stats["users"][str_user_id] = {
                "first_seen": current_time,
                "last_active": current_time,
                "username": username,
                "quizzes_created": 0
            }
        else:
            self.stats["users"][str_user_id]["last_active"] = current_time
            if username:
                self.stats["users"][str_user_id]["username"] = username

        self._save_stats()

    def record_quiz_creation(self, user_id):
        """Record when a user creates a quiz"""
        if "total_quizzes" not in self.stats:
            self.stats["total_quizzes"] = 0

        str_user_id = str(user_id)
        if str_user_id in self.stats.get("users", {}):
            self.stats["users"][str_user_id]["quizzes_created"] += 1
            self.stats["total_quizzes"] += 1
            self._save_stats()

    def get_active_users_count(self, days=7):
        """Get count of users active in the last X days"""
        cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
        active_users = sum(1 for user in self.stats.get("users", {}).values()
                          if user["last_active"] >= cutoff_time)
        return active_users

    def get_total_users_count(self):
        """Get total number of users"""
        return len(self.stats.get("users", {}))

    def get_total_quizzes_count(self):
        """Get total number of quizzes created"""
        return self.stats.get("total_quizzes", 0)

    def get_stats_message(self):
        """Get formatted statistics message"""
        return f"""📊 إحصائيات البوت:

👥 عدد المستخدمين الكلي: {self.get_total_users_count()}
👤 المستخدمين النشطين: {self.get_active_users_count()}
📝 عدد الاختبارات المنشأة: {self.get_total_quizzes_count()}"""