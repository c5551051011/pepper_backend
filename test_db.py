from core.database import engine, SessionLocal
from sqlalchemy import text


def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            print("✅ Database connection successful!")
            print(f"PostgreSQL version: {result.fetchone()[0]}")

        # Test session
        db = SessionLocal()
        result = db.execute(text("SELECT count(*) FROM users")).fetchone()
        print(f"✅ Users in database: {result[0]}")
        db.close()

    except Exception as e:
        print(f"❌ Database connection failed: {e}")


if __name__ == "__main__":
    test_connection()