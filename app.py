import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, User, Product, CartItem, Order, OrderItem

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://root:Shree@123@localhost/ecom-simple-flask'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def init_db() -> None:
    """Initialize database with tables and sample data"""
    with app.app_context():
        db.create_all()
        
        # Add sample products if none exist
        if Product.query.first() is None:
            products = [
                Product(name="T-Shirt", description="Comfort cotton T-shirt", price_cents=1999, image_url="https://via.placeholder.com/150"),
                Product(name="Mug", description="Ceramic coffee mug", price_cents=1299, image_url="https://via.placeholder.com/150"),
                Product(name="Notebook", description="A5 dotted notebook", price_cents=999, image_url="https://via.placeholder.com/150"),
                Product(name="Stickers Pack", description="Set of 10 stickers", price_cents=499, image_url="https://via.placeholder.com/150"),
            ]
            db.session.add_all(products)
            db.session.commit()
            print("✓ Sample products added to database")


init_db()


def current_user_id() -> int | None:
    return session.get("user_id")


def format_price(price_cents: int) -> str:
    return f"Rs{price_cents / 100:.2f}"


def get_cart_count() -> int:
    uid = current_user_id()
    if not uid:
        return 0
    total = db.session.query(db.func.sum(CartItem.quantity)).filter(
        CartItem.user_id == uid
    ).scalar()
    return int(total) if total else 0


@app.context_processor
def inject_template_helpers():
    return {"format_price": format_price, "get_cart_count": get_cart_count, "session": session}


@app.get("/")
def index():
    if current_user_id():
        return redirect(url_for("products"))
    return redirect(url_for("login_get"))


@app.get("/login")
def login_get():
    phone = (request.args.get("phone") or "").strip()
    return render_template("login.html", phone=phone)


@app.post("/login")
def login_post():
    phone = (request.form.get("phone") or "").strip()
    password = (request.form.get("password") or "").strip()

    if not phone:
        flash("Phone is required.", "error")
        return render_template("login.html", phone=phone)

    user = User.query.filter_by(phone=phone).first()
    if user is None:
        flash("User not found. Please create an account.", "error")
        return redirect(url_for("signup_get", phone=phone))
    
    if user.password != password:
        flash("Incorrect password.", "error")
        print(f"Login failed for phone: {phone} - incorrect password")
        return render_template("login.html", phone=phone)

    session["user_id"] = user.id
    session["phone"] = phone
    flash("Logged in.", "success")
    return redirect(url_for("products"))


@app.get("/signup")
def signup_get():
    phone = (request.args.get("phone") or "").strip()
    return render_template("signup.html", phone=phone)


@app.post("/signup")
def signup_post():
    phone = (request.form.get("phone") or "").strip()
    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()

    if not phone:
        flash("Phone is required.", "error")
        return redirect(url_for("signup_get", phone=phone))

    existing_user = User.query.filter_by(phone=phone).first()
    if existing_user is not None:
        flash("User already exists. Please log in.", "error")
        return redirect(url_for("login_get", phone=phone))

    user = User(name=username, phone=phone, password=password, created_at=datetime.datetime.utcnow())
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    session["phone"] = phone
    flash("Account created. Logged in.", "success")
    return redirect(url_for("products"))


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_get"))


@app.get("/products")
def products():
    items = Product.query.all()
    return render_template("products.html", products=items)


@app.post("/cart/add")
def cart_add():
    if not current_user_id():
        return jsonify({"ok": False, "error": "not_authenticated"}), 401

    data = request.get_json(silent=True) or request.form
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "invalid_input"}), 400

    if quantity <= 0:
        return jsonify({"ok": False, "error": "invalid_quantity"}), 400

    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"ok": False, "error": "product_not_found"}), 404

    cart_item = CartItem.query.filter_by(
        user_id=current_user_id(),
        product_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user_id(),
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    cart_count = get_cart_count()

    return jsonify({"ok": True, "cart_count": cart_count})


@app.get("/cart")
def cart_view():
    if not current_user_id():
        return redirect(url_for("login_get"))

    cart_items = db.session.query(CartItem, Product).filter(
        CartItem.user_id == current_user_id(),
        CartItem.product_id == Product.id
    ).all()
    
    items = [
        {
            "product_id": ci.CartItem.product_id,
            "quantity": ci.CartItem.quantity,
            "name": ci.Product.name,
            "price_cents": ci.Product.price_cents,
            "image_url": ci.Product.image_url,
        }
        for ci in cart_items
    ]
    
    total_cents = sum(item["price_cents"] * item["quantity"] for item in items)
    return render_template("cart.html", items=items, total_cents=total_cents)


@app.post("/checkout")
def checkout():
    if not current_user_id():
        return redirect(url_for("login_get"))

    cart_items = db.session.query(CartItem, Product).filter(
        CartItem.user_id == current_user_id(),
        CartItem.product_id == Product.id
    ).all()

    if not cart_items:
        flash("Cart is empty.", "error")
        return redirect(url_for("cart_view"))

    total_cents = sum(ci.Product.price_cents * ci.CartItem.quantity for ci in cart_items)

    order = Order(
        user_id=current_user_id(),
        total_cents=total_cents,
        payment_method="COD",
        status="placed",
        created_at=datetime.datetime.utcnow()
    )
    db.session.add(order)
    db.session.flush()

    for ci in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=ci.CartItem.product_id,
            quantity=ci.CartItem.quantity,
            price_cents=ci.Product.price_cents
        )
        db.session.add(order_item)

    CartItem.query.filter_by(user_id=current_user_id()).delete()
    db.session.commit()

    return render_template("order_success.html", order_id=order.id, total_cents=total_cents)


@app.get("/orders")
def orders_history():
    if not current_user_id():
        return redirect(url_for("login_get"))

    orders_list = Order.query.filter_by(user_id=current_user_id()).order_by(Order.id.desc()).all()
    
    orders = []
    for order in orders_list:
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        order_data = {
            "id": order.id,
            "total_cents": order.total_cents,
            "payment_method": order.payment_method,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else "",
            "items": [
                {
                    "product_id": oi.product_id,
                    "name": oi.product.name,
                    "quantity": oi.quantity,
                    "price_cents": oi.price_cents,
                }
                for oi in order_items
            ]
        }
        orders.append(order_data)

    return render_template("orders.html", orders=orders)


if __name__ == "__main__":
    print("=" * 60)
    print("Flask app starting...")
    print("Open http://localhost:8000 in your browser")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)