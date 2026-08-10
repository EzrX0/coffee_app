# Full-Stack Coffee App ☕

A beautiful, full-stack mobile application for browsing, favoriting, and ordering coffee. 

This project consists of a sleek frontend mobile app built with Flutter and a robust backend API built with Python, FastAPI, and PostgreSQL.

## Features ✨
- **Dynamic Coffee Catalog:** Browse coffees pulled directly from a live PostgreSQL database.
- **Search & Filter:** Search for specific coffees by name or filter by category (e.g., Cappuccino, Latte, Machiato).
- **Favorites System:** Save your favorite drinks and view them on a dedicated Favorites page.
- **Cart & Ordering:** Add coffees to your cart, select sizes, adjust quantities, and see a dynamically calculated total price on the Order page.
- **Global State Management:** Uses Flutter's `provider` package to ensure the UI updates instantly across all pages when you add an item to your cart or favorites.

## Tech Stack 🛠️
### Frontend
- **Framework:** Flutter / Dart
- **State Management:** Provider
- **Networking:** HTTP package (`http`)

### Backend
- **Framework:** Python / FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic

---

## Getting Started 🚀

To get this project up and running on your local machine, follow these steps:

### 1. Backend Setup (Python)
1. Ensure you have **Python 3.10+** and **PostgreSQL** installed on your machine.
2. Create a new PostgreSQL database named `coffee_db`.
3. Open a terminal in the `backend/` directory.
4. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. *(Optional)* If your PostgreSQL username/password is not the default `postgres:postgres`, update the connection URL in `backend/database.py`.
6. Start the FastAPI server:
   ```bash
   python -m uvicorn main:app --reload
   ```
   *The server will start at `http://127.0.0.1:8000` and automatically populate the database with initial coffee data!*

### 2. Frontend Setup (Flutter)
1. Open a new terminal in the `my_app/` directory.
2. Fetch the Flutter packages:
   ```bash
   flutter pub get
   ```
3. **Note on Emulators:** If you are running the app on an Android Emulator, the API URL is set to `http://10.0.2.2:8000` in `lib/providers/app_provider.dart`. If you are running on iOS, Web, or Windows Desktop, change this URL to `http://127.0.0.1:8000`.
4. Run the app:
   ```bash
   flutter run
   ```

## API Documentation 📚
FastAPI automatically generates interactive API documentation. With the backend running, you can visit:
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
