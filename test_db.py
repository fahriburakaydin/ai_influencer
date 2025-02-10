from database import init_db, save_post

def test_database():
    init_db()
    save_post("test", "test idea", "test.jpg", "test caption")
    print("Database test successful!")

if __name__ == "__main__":
    test_database()
    print()