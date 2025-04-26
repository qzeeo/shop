from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import json
import requests
from config import TELEGRAM_API_KEY, COINBASE_COMMERCE_API_KEY

# Global variables for orders and products
orders = []
products = []

# Load products from the products.json file
def load_products():
    global products
    with open('products.json', 'r') as f:
        products = json.load(f)["products"]

# Load orders from the orders.json file
def load_orders():
    global orders
    with open('orders.json', 'r') as f:
        orders = json.load(f)["orders"]

# Start command for the bot
def start(update, context):
    update.message.reply_text(
        "Welcome to Request Services Shop! Browse our digital goods and purchase easily."
    )

# Browse products
def browse(update, context):
    load_products()
    product_list = "\n".join([f"{product['id']}. {product['name']} - ${product['price']}" for product in products])
    update.message.reply_text(f"Available products:\n{product_list}\n\nUse /order <product_id> to buy.")

# Order command to initiate a purchase
def order(update, context):
    user_id = update.message.from_user.id
    if not context.args:
        update.message.reply_text("Please specify a product ID to order.")
        return
    product_id = int(context.args[0])

    # Check if the product exists
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        update.message.reply_text("Product not found!")
        return

    # Create an order
    order = {"user_id": user_id, "product_id": product_id, "status": "pending"}
    orders.append(order)
    save_orders()

    update.message.reply_text(f"Order for {product['name']} has been placed! Please complete payment.")

# Admin panel for managing products
def admin_panel(update, context):
    if update.message.from_user.id != YOUR_ADMIN_ID:
        update.message.reply_text("You are not authorized to use this command.")
        return

    command = context.args[0] if context.args else None
    if command == "add":
        name = context.args[1]
        price = float(context.args[2])
        product_id = len(products) + 1
        products.append({"id": product_id, "name": name, "price": price})
        save_products()
        update.message.reply_text(f"Product {name} added with ID {product_id}.")
    elif command == "remove":
        product_id = int(context.args[1])
        products[:] = [p for p in products if p['id'] != product_id]
        save_products()
        update.message.reply_text(f"Product with ID {product_id} removed.")
    else:
        update.message.reply_text("Invalid command for admin.")

# Save orders to orders.json
def save_orders():
    with open('orders.json', 'w') as f:
        json.dump({"orders": orders}, f, indent=4)

# Save products to products.json
def save_products():
    with open('products.json', 'w') as f:
        json.dump({"products": products}, f, indent=4)

# Webhook to send payment proof after Coinbase payment is confirmed
def send_proof(update, context):
    order_id = int(context.args[0]) if context.args else None
    if not order_id:
        update.message.reply_text("Please provide an order ID to send proof.")
        return
    order = next((o for o in orders if o["user_id"] == update.message.from_user.id and o["status"] == "paid"), None)
    if not order:
        update.message.reply_text("No paid orders found.")
        return
    product = next((p for p in products if p['id'] == order["product_id"]), None)
    update.message.reply_text(f"Payment proof for your order: {product['name']} - Order ID: {order_id}")

# Main function to start the bot
def main():
    updater = Updater(TELEGRAM_API_KEY, use_context=True)
    dispatcher = updater.dispatcher
    load_products()
    load_orders()

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("browse", browse))
    dispatcher.add_handler(CommandHandler("order", order))
    dispatcher.add_handler(CommandHandler("admin", admin_panel))
    dispatcher.add_handler(CommandHandler("sendproof", send_proof))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
