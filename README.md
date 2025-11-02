# 🎬 Film Manager System

A comprehensive Python-based film/show management system built with Object-Oriented Programming (OOP) principles. Manage your personal watchlist, track watched shows, get personalized recommendations, and analyze your viewing statistics.

## 📋 Table of Contents
- [Overview]
- [Features]
- [Technologies & Libraries]
- [OOP Concepts Used]
- [Installation]
- [Usage]
- [File Structure]
- [Data Persistence]
- [Examples]

## 🎯 Overview

Film Manager is a command-line application that helps users organize and track their film and TV show watching experience. Whether you're a casual viewer or a cinema enthusiast, this system provides an intuitive way to manage your entertainment library, maintain watchlists, rate content, and receive personalized recommendations based on your viewing habits.

## ✨ Features

### Core Functionalities

1. **User Management**
   - Create multiple user profiles
   - View all registered users
   - Track individual user statistics

2. **Show Library**
   - Add films/shows with details (title, genre, duration, rating)
   - Browse complete show catalog
   - Search shows by title (case-insensitive)

3. **Watchlist Management**
   - Add shows to personal watchlist
   - View watchlist for any user
   - Remove shows when marking as watched

4. **Watch History**
   - Mark shows as watched
   - Rate watched shows (0-10 scale)
   - Track viewing history

5. **Personalized Recommendations**
   - Get show recommendations based on favorite genres
   - Sorted by rating for quality suggestions
   - Excludes already watched/watchlisted shows

6. **Statistics & Analytics**
   - Total watch time (minutes and hours)
   - Genre distribution with percentages
   - Average rating given by user
   - Comprehensive viewing insights

7. **Data Persistence**
   - Auto-save after every operation
   - Load existing data on startup
   - JSON-based storage
   - View raw data file

## 🛠 Technologies & Libraries

### Standard Python Libraries

```python
import json          # Data serialization and persistence
import os            # File path operations
import functools     # Decorator implementation
from datetime import datetime    # Timestamp logging
from typing import List, Dict, Optional  # Type hints
from collections import Counter  # Genre distribution analysis
```

### Python Version
- **Python 3.7+** (required for type hints and modern features)

### No External Dependencies
This project uses only Python standard library modules, making it lightweight and easy to deploy without additional package installations.

## 🏗 OOP Concepts Used

### 1. **Classes and Objects**
- `Show`: Represents a film/TV show entity
- `User`: Represents a user with personal data
- `ShowManager`: Main controller managing the system
- `DataPersistence`: Context manager for file operations

### 2. **Encapsulation**
```python
class User:
    def __init__(self, username: str):
        self._username = username      # Private attributes
        self._watchlist: List[Show] = []
        self._watched: Dict[Show, Optional[float]] = {}
    
    @property
    def username(self) -> str:         # Property decorator
        return self._username
```

### 3. **Properties (Getters/Setters)**
- Read-only properties: `title`, `genre`, `username`
- Validated setters: `rating` (ensures 0-10 range)

### 4. **Dunder Methods (Magic Methods)**
- `__init__`: Constructor
- `__str__`: String representation for users
- `__repr__`: Developer-friendly representation
- `__eq__`: Equality comparison
- `__hash__`: Make objects hashable
- `__lt__`: Less-than comparison for sorting
- `__len__`: Length calculation
- `__bool__`: Boolean evaluation

### 5. **Decorators**
```python
@log_action
def add_to_watchlist(self, show: Show):
    # Automatically logs actions with timestamps
```

### 6. **Context Managers**
```python
class DataPersistence:
    def __enter__(self):
        # Resource acquisition
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Resource cleanup
```

### 7. **Composition**
- `ShowManager` contains `Show` and `User` objects
- `User` contains list of `Show` objects

### 8. **Class Methods**
```python
@classmethod
def from_dict(cls, data: Dict) -> 'Show':
    # Alternative constructor from dictionary
```

### 9. **Type Hints**
- Function parameters and return types
- Collection types (List, Dict, Optional)
- Improved code readability and IDE support


## 🚀 Usage

### Starting the Program

```bash
python Film_Manager.py
```

You'll see:
```
============================================================
FILM MANAGER SYSTEM
============================================================

Choose how to start:
1. Run Quick Demo (see the system in action)
2. Start Normal Program

Enter choice (1 or 2):
```

### Main Menu Options

```
--- MAIN MENU ---
1. Create User
2. Add Show
3. List All Shows
4. List All Users
5. Add Show to User's Watchlist
6. View User's Watchlist
7. Mark Show as Watched
8. Show Recommendations
9. Show User Statistics
10. View Saved Data File
11. Save Data
12. Exit
0. RUN QUICK DEMO
```

### Quick Demo

Option `0` runs an automated demonstration showing all features:
- Creates sample shows
- Creates a user
- Adds shows to watchlist
- Marks shows as watched
- Shows statistics and recommendations

### Typical Workflow

1. **Create a User**
   - Select option `1`
   - Enter username: `Alice`

2. **Add Shows to Library**
   - Select option `2`
   - Enter: Title, Genre, Duration (minutes), Rating (0-10)

3. **Add Shows to Watchlist**
   - Select option `5`
   - Enter username
   - Enter show number or title

4. **Mark as Watched**
   - Select option `7`
   - Enter username
   - Select show from watchlist
   - Rate the show (optional)

5. **View Statistics**
   - Select option `9`
   - Enter username
   - See complete viewing stats

## 📁 File Structure

```
film-manager/
│
├── Film_Manager.py           # Main application file
├── show_manager_data.json    # Auto-generated data storage
└── README.md                 # This file
```

### Code Structure

```python
# Decorators
log_action()                  # Logging decorator

# Context Manager
DataPersistence               # Safe file operations

# Entity Classes
Show                          # Film/Show representation
User                          # User profile management

# Manager Class
ShowManager                   # Main controller

# Utility Functions
quick_demo()                  # Demonstration function
main()                        # Main program loop
```

## 💾 Data Persistence

### Automatic Saving
Data is automatically saved after:
- Creating a user
- Adding a show
- Adding to watchlist
- Marking as watched

### Data Format (JSON)

```json
{
  "shows": [
    {
      "title": "Inception",
      "genre": "Sci-Fi",
      "duration": 148,
      "rating": 8.8,
      "user_ratings": []
    }
  ],
  "users": [
    {
      "username": "Alice",
      "watchlist": [...],
      "watched": [...]
    }
  ]
}
```

### Data Loading
- Automatically loads on program start
- Validates JSON structure
- Handles corrupted files gracefully

## 📝 Examples

### Example 1: Adding a Show
```
Enter your choice (0-12): 2
Enter show title: The Shawshank Redemption
Enter genre: Drama
Enter duration (minutes): 142
Enter initial rating (0-10, default 0): 9.3
[OK] Show added: The Shawshank Redemption (Drama) - 142min - Rating: 9.3/10
```

### Example 2: Adding to Watchlist
```
Enter your choice (0-12): 5
Enter username: Alice

============================================================
ALL AVAILABLE SHOWS
============================================================
1. The Shawshank Redemption (Drama) - 142min - Rating: 9.3/10
2. Inception (Sci-Fi) - 148min - Rating: 8.8/10
============================================================

Enter show number or title to add to watchlist: 1
[OK] 'The Shawshank Redemption' added to Alice's watchlist
```

### Example 3: Viewing Statistics
```
Enter your choice (0-12): 9
Enter username: Alice

============================================================
STATISTICS FOR ALICE
============================================================
Total shows watched: 5
Shows in watchlist: 3
Total watch time: 720 minutes (12.0 hours)
Average rating given: 8.8/10

Genre Distribution:
  - Sci-Fi: 3 shows (60.0%)
  - Drama: 2 shows (40.0%)
============================================================
```

### Example 4: Getting Recommendations
```
Enter your choice (0-12): 8
Enter username: Alice

============================================================
RECOMMENDATIONS FOR ALICE (Genre: Sci-Fi)
============================================================
1. Interstellar (Sci-Fi) - 169min - Rating: 8.6/10
2. The Matrix (Sci-Fi) - 136min - Rating: 8.7/10
============================================================
```

## 🎓 Educational Value

This project demonstrates:

✅ **OOP Best Practices**
- Proper class design and separation of concerns
- Encapsulation and data hiding
- Use of properties and decorators

✅ **Python Features**
- Type hints for better code quality
- Context managers for resource management
- List/dict comprehensions
- Lambda functions

✅ **Software Design Patterns**
- Composition over inheritance
- Separation of concerns
- Single Responsibility Principle

✅ **Data Management**
- JSON serialization/deserialization
- Data validation
- Error handling

✅ **User Experience**
- Intuitive menu system
- Input validation
- Helpful error messages
- Auto-save functionality

## 🔧 Customization

### Adding New Genres
Simply enter the new genre when adding a show - no code changes needed!

### Changing Data File Location
```python
manager = ShowManager(data_file='custom_path/my_data.json')
```

### Adjusting Recommendation Limit
```python
manager.get_recommendations(username, limit=10)  # Default is 5
```

## 🐛 Troubleshooting

### Data File Not Loading
- Check if `show_manager_data.json` exists
- Verify JSON syntax is valid
- Delete file to start fresh if corrupted

### Unicode Characters Not Displaying
- Ensure terminal supports UTF-8 encoding
- Check Python's default encoding: `sys.getdefaultencoding()`

### Users Not Found
- Check spelling (case-insensitive)
- Use option `4` to list all users
- Create user first if none exist

## 📄 License

This project is open source and available for educational purposes.

## 👥 Contributing

Feel free to fork, modify, and enhance this project. Suggestions for improvements:
- Add GUI interface (Tkinter/PyQt)
- Implement search and filter features
- Add movie poster display
- Integration with online databases (IMDB, TMDB)
- Export statistics to PDF/Excel
- Multi-language support

## 📧 Contact

For questions or suggestions, please open an issue in the repository.

---

**Happy Watching! 🎬🍿**
