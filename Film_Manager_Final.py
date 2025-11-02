import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from collections import Counter
import functools


# Decorator for logging actions
def log_action(func):
    """Decorator to log user actions with timestamp"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = func(*args, **kwargs)
        print(f"[{timestamp}] Action: {func.__name__} completed")
        return result

    return wrapper


# Context Manager for file operations
class DataPersistence:
    """Context manager for safe file operations"""

    def __init__(self, filename: str, mode: str = 'r'):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        try:
            self.file = open(self.filename, self.mode, encoding='utf-8')
            return self.file
        except FileNotFoundError:
            if 'r' in self.mode:
                return None
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False


class Show:
    """Represents a film/show with its properties"""

    def __init__(self, title: str, genre: str, duration: int, rating: float = 0.0):
        self._title = title
        self._genre = genre
        self._duration = duration  # in minutes
        self._rating = rating
        self._user_ratings = []

    # Encapsulation with properties
    @property
    def title(self):
        return self._title

    @property
    def genre(self):
        return self._genre

    @property
    def duration(self):
        return self._duration

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value: float):
        if 0 <= value <= 10:
            self._rating = value
        else:
            raise ValueError("Rating must be between 0 and 10")

    def add_user_rating(self, rating: float):
        """Add a user rating and update average"""
        if 0 <= rating <= 10:
            self._user_ratings.append(rating)
            self._rating = sum(self._user_ratings) / len(self._user_ratings)
        else:
            raise ValueError("Rating must be between 0 and 10")

    # Dunder methods
    def __repr__(self) -> str:
        return f"Show('{self._title}', '{self._genre}', {self._duration}min, {self._rating:.1f})"

    def __str__(self) -> str:
        return f"{self._title} ({self._genre}) - {self._duration}min - Rating: {self._rating:.1f}/10"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Show):
            return False
        return self._title.lower() == other._title.lower()

    def __hash__(self) -> int:
        """Make Show hashable for use in dictionaries"""
        return hash(self._title.lower())

    def __lt__(self, other) -> bool:
        """For sorting by rating"""
        return self._rating < other._rating

    def __bool__(self) -> bool:
        """Always True for boolean checks"""
        return True

    def to_dict(self) -> Dict:
        """Convert show to dictionary for JSON serialization"""
        return {
            'title': self._title,
            'genre': self._genre,
            'duration': self._duration,
            'rating': self._rating,
            'user_ratings': self._user_ratings
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Show':
        """Create Show instance from dictionary"""
        show = cls(data['title'], data['genre'], data['duration'], data['rating'])
        show._user_ratings = data.get('user_ratings', [])
        return show


class User:
    """Represents a user with watchlist and watched history"""

    def __init__(self, username: str):
        self._username = username
        self._watchlist: List[Show] = []
        self._watched: Dict[Show, Optional[float]] = {}  # Show: user_rating

    @property
    def username(self) -> str:
        return self._username

    @property
    def watchlist(self) -> List[Show]:
        return self._watchlist.copy()

    @property
    def watched(self) -> Dict[Show, Optional[float]]:
        return self._watched.copy()

    @log_action
    def add_to_watchlist(self, show: Show):
        """Add show to user's watchlist"""
        # Check if already in watchlist
        if any(s.title.lower() == show.title.lower() for s in self._watchlist):
            print(f"[X] '{show.title}' is already in watchlist")
            return False

        # Check if already watched
        if any(s.title.lower() == show.title.lower() for s in self._watched.keys()):
            print(f"[X] '{show.title}' is already watched")
            return False

        self._watchlist.append(show)
        print(f"[OK] '{show.title}' added to {self._username}'s watchlist")
        return True

    @log_action
    def mark_as_watched(self, show: Show, user_rating: Optional[float] = None):
        """Mark show as watched and optionally rate it"""
        # Remove from watchlist if present
        self._watchlist = [s for s in self._watchlist if s.title.lower() != show.title.lower()]

        # Add to watched
        self._watched[show] = user_rating

        if user_rating is not None:
            show.add_user_rating(user_rating)
            print(f"[OK] '{show.title}' marked as watched with rating: {user_rating}/10")
        else:
            print(f"[OK] '{show.title}' marked as watched")
        return True

    def get_total_watch_time(self) -> int:
        """Calculate total time spent watching (in minutes)"""
        return sum(show.duration for show in self._watched.keys())

    def get_genre_distribution(self) -> Dict[str, int]:
        """Get distribution of watched genres"""
        genres = [show.genre for show in self._watched.keys()]
        return dict(Counter(genres))

    def get_average_rating_given(self) -> float:
        """Calculate average rating given by user"""
        ratings = [r for r in self._watched.values() if r is not None]
        return sum(ratings) / len(ratings) if ratings else 0.0

    # Dunder methods
    def __repr__(self) -> str:
        return f"User('{self._username}', watchlist={len(self._watchlist)}, watched={len(self._watched)})"

    def __str__(self) -> str:
        return f"User: {self._username} | Watchlist: {len(self._watchlist)} | Watched: {len(self._watched)}"

    def __len__(self) -> int:
        """Return total number of shows (watchlist + watched)"""
        return len(self._watchlist) + len(self._watched)

    def __bool__(self) -> bool:
        """Always True for boolean checks - user object always exists"""
        return True

    def to_dict(self) -> Dict:
        """Convert user to dictionary for JSON serialization"""
        return {
            'username': self._username,
            'watchlist': [show.to_dict() for show in self._watchlist],
            'watched': [
                {'show': show.to_dict(), 'user_rating': rating}
                for show, rating in self._watched.items()
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict, all_shows: Dict[str, Show]) -> 'User':
        """Create User instance from dictionary"""
        user = cls(data['username'])

        # Restore watchlist
        for show_data in data.get('watchlist', []):
            show_title = show_data['title']
            # Use existing show from library or create new one
            if show_title in all_shows:
                show = all_shows[show_title]
            else:
                show = Show.from_dict(show_data)
                all_shows[show_title] = show
            user._watchlist.append(show)

        # Restore watched
        for item in data.get('watched', []):
            show_data = item['show']
            show_title = show_data['title']
            # Use existing show from library or create new one
            if show_title in all_shows:
                show = all_shows[show_title]
            else:
                show = Show.from_dict(show_data)
                all_shows[show_title] = show
            user._watched[show] = item['user_rating']

        return user


class ShowManager:
    """Main manager class that coordinates shows and users (Composition pattern)"""

    def __init__(self, data_file: str = 'show_manager_data.json'):
        self._shows: Dict[str, Show] = {}  # title: Show
        self._users: Dict[str, User] = {}  # username: User
        self._data_file = data_file
        self.load_data()

    @log_action
    def add_show(self, title: str, genre: str, duration: int, rating: float = 0.0):
        """Add a new show to the library"""
        if title in self._shows:
            print(f"[X] Show '{title}' already exists")
            return

        show = Show(title, genre, duration, rating)
        self._shows[title] = show
        print(f"[OK] Show added: {show}")
        self.save_data()

    @log_action
    def create_user(self, username: str):
        """Create a new user"""
        if username in self._users:
            print(f"[X] User '{username}' already exists")
            return

        user = User(username)
        self._users[username] = user
        print(f"[OK] User created: {user}")
        self.save_data()

    def get_user(self, username: str) -> Optional[User]:
        """Get user by username (case-insensitive with suggestions)"""
        # Try exact match first
        if username in self._users:
            return self._users[username]

        # Try case-insensitive match
        for user_name, user in self._users.items():
            if user_name.lower() == username.lower():
                return user

        # User not found - suggest similar usernames
        print(f"[X] User '{username}' not found")
        if self._users:
            print(f"\nAvailable users:")
            for i, user_name in enumerate(self._users.keys(), 1):
                print(f"  {i}. {user_name}")
        else:
            print("No users exist yet. Create a user first (Option 1)")

        return None

    def get_show(self, title: str) -> Optional[Show]:
        """Get show by title (case-insensitive)"""
        # Try exact match first
        if title in self._shows:
            return self._shows[title]

        # Try case-insensitive match
        for show_title, show in self._shows.items():
            if show_title.lower() == title.lower():
                return show

        return None

    def list_all_shows(self):
        """Display all available shows"""
        if not self._shows:
            print("No shows available in the library")
            return

        print("\n" + "=" * 60)
        print("ALL AVAILABLE SHOWS")
        print("=" * 60)
        for i, show in enumerate(sorted(self._shows.values(), reverse=True), 1):
            print(f"{i}. {show}")
        print("=" * 60)

    def list_all_users(self):
        """Display all users"""
        if not self._users:
            print("No users in the system")
            return

        print("\n" + "=" * 60)
        print("ALL USERS")
        print("=" * 60)
        for i, user in enumerate(self._users.values(), 1):
            print(f"{i}. {user}")
        print("=" * 60)

    def view_user_watchlist(self, username: str):
        """Display user's watchlist"""
        user = self.get_user(username)
        if user is None:
            return

        watchlist = user.watchlist
        if not watchlist:
            print(f"\n{username}'s watchlist is empty")
            return

        print(f"\n{'=' * 60}")
        print(f"{username.upper()}'S WATCHLIST")
        print("=" * 60)
        for i, show in enumerate(watchlist, 1):
            print(f"{i}. {show}")
        print("=" * 60)

    def add_show_to_watchlist(self, username: str):
        """Add a show to user's watchlist (complete workflow)"""
        user = self.get_user(username)
        if user is None:
            return

        # Show available shows
        self.list_all_shows()

        if not self._shows:
            print("[X] No shows available. Add shows first (Option 2)")
            return

        show_title = input("\nEnter show title to add to watchlist: ").strip()
        if not show_title:
            print("[X] No show title entered")
            return

        show = self.get_show(show_title)

        if show is None:
            print(f"[X] Show '{show_title}' not found")
            return

        # Add to watchlist
        if user.add_to_watchlist(show):
            self.save_data()

    def mark_show_as_watched(self, username: str):
        """Mark a show as watched (complete workflow)"""
        user = self.get_user(username)
        if user is None:
            return

        # Show user's watchlist
        self.view_user_watchlist(username)

        watchlist = user.watchlist
        if not watchlist:
            print("\n[X] Watchlist is empty. Add shows to watchlist first (Option 5)")
            return

        show_title = input("\nEnter show title to mark as watched: ").strip()
        if not show_title:
            print("[X] No show title entered")
            return

        show = self.get_show(show_title)

        if show is None:
            print(f"[X] Show '{show_title}' not found")
            return

        # Get rating
        try:
            rating_input = input("Enter your rating (0-10, or press Enter to skip): ").strip()
            rating = float(rating_input) if rating_input else None
            if rating is not None and (rating < 0 or rating > 10):
                print("[X] Invalid rating. Must be between 0 and 10.")
                return
        except ValueError:
            print("[X] Invalid rating format.")
            return

        # Mark as watched
        if user.mark_as_watched(show, rating):
            self.save_data()

    def get_recommendations(self, username: str, limit: int = 5):
        """Recommend shows based on user's watched genres"""
        user = self.get_user(username)
        if user is None:
            return

        # Get user's favorite genres
        genre_dist = user.get_genre_distribution()
        if not genre_dist:
            print("\n[X] Watch some shows first to get personalized recommendations!")
            return

        favorite_genre = max(genre_dist, key=genre_dist.get)

        # Find unwatched shows in favorite genre
        watched_titles = {show.title.lower() for show in user.watched.keys()}
        watchlist_titles = {show.title.lower() for show in user.watchlist}

        recommendations = [
            show for show in self._shows.values()
            if show.genre == favorite_genre
               and show.title.lower() not in watched_titles
               and show.title.lower() not in watchlist_titles
        ]

        # Sort by rating
        recommendations.sort(reverse=True)
        recommendations = recommendations[:limit]

        if not recommendations:
            print(f"\n[X] No recommendations available in your favorite genre: {favorite_genre}")
            return

        print(f"\n{'=' * 60}")
        print(f"RECOMMENDATIONS FOR {username.upper()} (Genre: {favorite_genre})")
        print("=" * 60)
        for i, show in enumerate(recommendations, 1):
            print(f"{i}. {show}")
        print("=" * 60)

    def show_user_statistics(self, username: str):
        """Display user statistics"""
        user = self.get_user(username)
        if user is None:
            return

        total_time = user.get_total_watch_time()
        genre_dist = user.get_genre_distribution()
        avg_rating = user.get_average_rating_given()

        print(f"\n{'=' * 60}")
        print(f"STATISTICS FOR {username.upper()}")
        print("=" * 60)
        print(f"Total shows watched: {len(user.watched)}")
        print(f"Shows in watchlist: {len(user.watchlist)}")
        print(f"Total watch time: {total_time} minutes ({total_time / 60:.1f} hours)")
        print(f"Average rating given: {avg_rating:.1f}/10")

        if genre_dist:
            print("\nGenre Distribution:")
            for genre, count in sorted(genre_dist.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(user.watched)) * 100
                print(f"  - {genre}: {count} shows ({percentage:.1f}%)")

        print("=" * 60)

    def save_data(self):
        """Save all data to JSON file using context manager"""
        data = {
            'shows': [show.to_dict() for show in self._shows.values()],
            'users': [user.to_dict() for user in self._users.values()]
        }

        try:
            with DataPersistence(self._data_file, 'w') as f:
                if f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"[OK] Data saved to {self._data_file}")
        except Exception as e:
            print(f"[X] Error saving data: {e}")

    def load_data(self):
        """Load data from JSON file using context manager"""
        with DataPersistence(self._data_file, 'r') as f:
            if f is None:
                print(f"[!] No existing data file found. Starting fresh.\n")
                return

            try:
                data = json.load(f)

                # Clear existing data
                self._shows.clear()
                self._users.clear()

                # Load shows first
                for show_data in data.get('shows', []):
                    show = Show.from_dict(show_data)
                    self._shows[show.title] = show

                # Load users with proper show references
                for user_data in data.get('users', []):
                    try:
                        user = User.from_dict(user_data, self._shows)
                        self._users[user.username] = user
                    except Exception as e:
                        print(f"[X] Error loading user {user_data.get('username', 'unknown')}: {e}")

                print(f"[OK] Data loaded successfully!")
                print(f"     Shows: {len(self._shows)}")
                print(f"     Users: {len(self._users)}")
                if self._users:
                    print(f"     Available users: {', '.join(self._users.keys())}")
                print()

            except json.JSONDecodeError as e:
                print(f"[X] Error loading data file: {e}. Starting fresh.\n")
            except Exception as e:
                print(f"[X] Unexpected error loading data: {e}. Starting fresh.\n")

    def view_saved_data(self):
        """Display the contents of the saved JSON file"""
        if not os.path.exists(self._data_file):
            print(f"[X] No data file found at: {self._data_file}")
            return

        print(f"\n{'=' * 60}")
        print(f"SAVED DATA FILE: {self._data_file}")
        print(f"File location: {os.path.abspath(self._data_file)}")
        print("=" * 60)

        with DataPersistence(self._data_file, 'r') as f:
            if f:
                content = f.read()
                print(content)
        print("=" * 60)

    def __len__(self) -> int:
        """Return total number of shows"""
        return len(self._shows)

    def __repr__(self) -> str:
        return f"ShowManager(shows={len(self._shows)}, users={len(self._users)})"


def quick_demo():
    """Quick demonstration of the system"""
    print("\n" + "=" * 60)
    print("FILM MANAGER - QUICK DEMO")
    print("=" * 60)

    # Create manager
    manager = ShowManager()

    # Add some sample shows
    print("\n--- Adding Sample Shows ---")
    manager.add_show("Inception", "Sci-Fi", 148, 8.8)
    manager.add_show("The Dark Knight", "Action", 152, 9.0)
    manager.add_show("Interstellar", "Sci-Fi", 169, 8.6)
    manager.add_show("Pulp Fiction", "Crime", 154, 8.9)
    manager.add_show("The Matrix", "Sci-Fi", 136, 8.7)

    # Create a user
    print("\n--- Creating User ---")
    manager.create_user("Alice")

    # Add shows to watchlist
    print("\n--- Adding to Watchlist ---")
    user = manager.get_user("Alice")
    if user is not None:
        user.add_to_watchlist(manager.get_show("Inception"))
        user.add_to_watchlist(manager.get_show("Interstellar"))
        user.add_to_watchlist(manager.get_show("The Matrix"))
        manager.save_data()

    # View watchlist
    print("\n--- Viewing Watchlist ---")
    manager.view_user_watchlist("Alice")

    # Mark some as watched
    print("\n--- Marking Shows as Watched ---")
    if user is not None:
        user.mark_as_watched(manager.get_show("Inception"), 9.5)
        user.mark_as_watched(manager.get_show("The Matrix"), 9.0)
        manager.save_data()

    # Show statistics
    print("\n--- User Statistics ---")
    manager.show_user_statistics("Alice")

    # Show recommendations
    print("\n--- Recommendations ---")
    manager.get_recommendations("Alice")

    print("\n" + "=" * 60)
    print("DEMO COMPLETED!")
    print("=" * 60)
    print("\nThe data has been saved to 'show_manager_data.json'")
    print("Run the program again to see the data persist!")


def main():
    """Main workflow cycle"""
    manager = ShowManager()

    print("=" * 60)
    print("WELCOME TO YOUR SHOW MANAGER!")
    print("=" * 60)

    while True:
        print("\n--- MAIN MENU ---")
        print("1. Create User")
        print("2. Add Show")
        print("3. List All Shows")
        print("4. List All Users")
        print("5. Add Show to User's Watchlist")
        print("6. View User's Watchlist")
        print("7. Mark Show as Watched")
        print("8. Show Recommendations")
        print("9. Show User Statistics")
        print("10. View Saved Data File")
        print("11. Save Data")
        print("12. Exit")
        print("0. RUN QUICK DEMO")

        choice = input("\nEnter your choice (0-12): ").strip()

        if choice == '0':
            quick_demo()
            break

        elif choice == '1':
            username = input("Enter username: ").strip()
            if username:
                manager.create_user(username)

        elif choice == '2':
            title = input("Enter show title: ").strip()
            genre = input("Enter genre: ").strip()
            try:
                duration = int(input("Enter duration (minutes): ").strip())
                rating = float(input("Enter initial rating (0-10, default 0): ").strip() or "0")
                manager.add_show(title, genre, duration, rating)
            except ValueError:
                print("[X] Invalid input. Please enter valid numbers.")

        elif choice == '3':
            manager.list_all_shows()

        elif choice == '4':
            manager.list_all_users()

        elif choice == '5':
            username = input("Enter username: ").strip()
            if username:
                manager.add_show_to_watchlist(username)

        elif choice == '6':
            username = input("Enter username: ").strip()
            if username:
                manager.view_user_watchlist(username)

        elif choice == '7':
            username = input("Enter username: ").strip()
            if username:
                manager.mark_show_as_watched(username)

        elif choice == '8':
            username = input("Enter username: ").strip()
            if username:
                manager.get_recommendations(username)

        elif choice == '9':
            username = input("Enter username: ").strip()
            if username:
                manager.show_user_statistics(username)

        elif choice == '10':
            manager.view_saved_data()

        elif choice == '11':
            manager.save_data()

        elif choice == '12':
            save_choice = input("Save data before exit? (y/n): ").strip().lower()
            if save_choice == 'y':
                manager.save_data()
            print("\nThank you for using Show Manager! Goodbye!")
            break

        else:
            print("[X] Invalid choice. Please select 0-12.")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FILM MANAGER SYSTEM")
    print("=" * 60)
    print("\nChoose how to start:")
    print("1. Run Quick Demo (see the system in action)")
    print("2. Start Normal Program")

    start_choice = input("\nEnter choice (1 or 2): ").strip()

    if start_choice == '1':
        quick_demo()
    else:
        main()