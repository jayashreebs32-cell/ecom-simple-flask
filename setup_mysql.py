#!/usr/bin/env python
"""
MySQL Database Setup Script
Creates the ecom-simple-flask schema and initializes tables
"""
import mysql.connector
from mysql.connector import Error

# MySQL connection details
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shree@123',
}

try:
    # Connect to MySQL
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # Create database/schema
    print("Creating database schema...")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS `ecom-simple-flask` DEFAULT CHARACTER SET utf8mb4")
    
    # Use the database
    cursor.execute("USE `ecom-simple-flask`")
    
    # Create tables
    print("Creating tables...")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        phone VARCHAR(20) UNIQUE NOT NULL,
        password VARCHAR(255),
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price_cents INT NOT NULL,
        image_url VARCHAR(500)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart_items (
        user_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL DEFAULT 1,
        PRIMARY KEY (user_id, product_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        total_cents INT NOT NULL,
        payment_method VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        price_cents INT NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    
    conn.commit()
    print("✓ Database schema created successfully!")
    print("✓ All tables created successfully!")
    
    cursor.close()
    conn.close()
    
except Error as e:
    print(f"✗ Error: {e}")
    exit(1)
