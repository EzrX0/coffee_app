import 'coffee_item.dart';

class CartItem {
  final int id;
  final int coffeeId;
  final String size;
  final int quantity;
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
}
