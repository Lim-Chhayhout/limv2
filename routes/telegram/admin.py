from teleBotpackage.sendText import send_text
from decimal import Decimal

def send_order_to_telegram(order):
    token = '7516838493:AAHLcnGZy5ntw6aQ_K1IRVW3NwHGdVS3QvU'
    chat_id = '@su413test'

    message = f"🚀 *New Order Received!* 🚀\n\n"
    message += f"🆔 *Order Number:* {order.order_number}\n"
    message += f"👤 *Customer:* {order.customer.name}\n"
    message += f"📧 *Email:* {order.customer.email}\n"
    message += f"📞 *Phone:* {order.customer.telephone}\n"
    message += f"🚚 *Shipping:* {order.shipping.type} (${order.shipping.cost})\n"
    message += f"💳 *Payment:* {order.payment.type}\n\n"
    message += "🛍️ *Products:*\n"

    for item in order.products_info:
        message += f"✨ {item['name']}({item['status']}) x{item['qty']} = ${'%.2f' % item['subtotal']}\n"

    total_amount = Decimal(order.total_amount)
    message += f"\n💰 *Total Amount:* ${'%.2f' % total_amount}\n"
    message += "🎉 Thank you for your order! 🎉"

    try:
        send_text(token, chat_id, message)
        print("Order sent to Telegram successfully")
    except Exception as e:
        print("Error sending order to Telegram:", e)
