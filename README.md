# Simple Ecom (Flask + MySQL + SQLAlchemy)

- A tiny e-commerce demo with MySQL database backend:
- Login with phone number + password (creates user if missing)
- Browse products (seeded)
- Add to cart
- Checkout with Cash on Delivery
- Order history tracking

## Tech Stack
- **Framework**: Flask 3.0+
- **Database**: MySQL with SQLAlchemy ORM
- **Driver**: PyMySQL
- **Python**: 3.10+

## Requirements
- Python 3.10+
- MySQL Server running locally (or update connection string in `.env`)

## Setup (Windows PowerShell)

### 1. Clone and Navigate
```powershell
cd C:\path\to\ecom-simple-flask
```

### 2. Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Initialize Database
```powershell
python setup_mysql.py
```
This creates the `ecom-simple-flask` schema and all tables in MySQL.

### 5. Run the App
```powershell
python app.py
```
Open `http://localhost:5000` in your browser.

## Setup (macOS/Linux)

### 1. Clone and Navigate
```bash
cd /path/to/ecom-simple-flask
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python setup_mysql.py
```

### 5. Run the App
```bash
python app.py
```
Open `http://localhost:5000` in your browser.

## Database Configuration

The app connects to MySQL using credentials in `.env`:
```
DATABASE_URL=mysql+pymysql://root:password@localhost/ecom-simple-flask
```

**Default Credentials:**
- Host: `localhost`
- User: `root`
- Password: `Shree@123`
- Database: `ecom-simple-flask`

To use different credentials, update the `.env` file before running `setup_mysql.py`.

## Database Schema

Tables created automatically:
- **users** - User accounts (phone, name, password, created_at)
- **products** - Product catalog (name, description, price_cents, image_url)
- **cart_items** - Shopping cart (user_id, product_id, quantity)
- **orders** - Order history (user_id, total_cents, payment_method, status, created_at)
- **order_items** - Order details (order_id, product_id, quantity, price_cents)

## Features

### Authentication
- Phone + password login/signup (demo only — passwords stored in plaintext for simplicity)
- Session-based user tracking

### Shopping
- Browse seeded products
- Add to cart with quantity
- Real-time cart count updates
- Checkout with COD payment method

### Orders
- Order confirmation page
- Order history with items
- Order tracking

## API Routes

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/` | Redirect to login/products |
| GET | `/login` | Login page |
| POST | `/login` | Process login |
| GET | `/signup` | Signup page |
| POST | `/signup` | Create new user |
| GET | `/logout` | Clear session |
| GET | `/products` | List all products |
| POST | `/cart/add` | Add item to cart |
| GET | `/cart` | View cart |
| POST | `/checkout` | Place order |
| GET | `/orders` | Order history |

## Notes

-- Passwords are stored in plaintext in this demo. Do NOT use in production.
- Set `SECRET_KEY` environment variable in production.
- MySQL must be running before starting the app.
- First run creates sample products automatically.
- To reset data, delete records from MySQL (app will still work).
- SQLAlchemy ORM provides type-safe database queries.

## Troubleshooting

**"Can't connect to MySQL server"**
- Ensure MySQL is running
- Check credentials in `.env`
- Verify host and port

**"ModuleNotFoundError: No module named..."**
- Activate virtual environment
- Run `pip install -r requirements.txt`

**"Table already exists"**
- Safe to ignore - `setup_mysql.py` uses `CREATE TABLE IF NOT EXISTS`
- Run it multiple times if needed