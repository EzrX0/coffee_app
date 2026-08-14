import 'coffee_item.dart';

class OrderItem {
  final int id;
  final int coffeeId;
  final String size;
  final int quantity;
  final double price;
  final CoffeeItem coffee;

  OrderItem({
    required this.id,
    required this.coffeeId,
    required this.size,
    required this.quantity,
    required this.price,
    required this.coffee,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      id: json['id'],
      coffeeId: json['coffee_id'],
      size: json['size'],
      quantity: json['quantity'],
      price: (json['price'] as num).toDouble(),
      coffee: CoffeeItem.fromJson(json['coffee']),
    );
  }
}

class Order {
  final int id;
  final double totalPrice;
  final DateTime createdAt;
  final List<OrderItem> items;

  Order({
    required this.id,
    required this.totalPrice,
    required this.createdAt,
    required this.items,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'],
      totalPrice: (json['total_price'] as num).toDouble(),
      createdAt: DateTime.parse(json['created_at']),
      items: (json['items'] as List).map((item) => OrderItem.fromJson(item)).toList(),
    );
  }
}
