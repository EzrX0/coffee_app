import 'coffee_item.dart';

class CartItem {
  final int id;
  final int coffeeId;
  final String size;
  int quantity;
  final CoffeeItem coffee;

  CartItem({
    required this.id,
    required this.coffeeId,
    required this.size,
    required this.quantity,
    required this.coffee,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      id: json['id'],
      coffeeId: json['coffee_id'],
      size: json['size'],
      quantity: json['quantity'],
      coffee: CoffeeItem.fromJson(json['coffee']),
    );
  }

  double get unitPrice {
    double basePrice = coffee.price;
    if (size == 'M') return basePrice + 0.50;
    if (size == 'L') return basePrice + 1.00;
    return basePrice;
  }

  double get totalPrice => unitPrice * quantity;
}
