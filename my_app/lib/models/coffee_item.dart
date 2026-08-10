class CoffeeItem {
  final int? id;
  final String name;
  final String subtitle;
  final double price;
  final double rating;
  final String imageUrl;

  const CoffeeItem({
    this.id,
    required this.name,
    required this.subtitle,
    required this.price,
    required this.rating,
    required this.imageUrl,
  });

  factory CoffeeItem.fromJson(Map<String, dynamic> json) {
    return CoffeeItem(
      id: json['id'],
      name: json['name'],
      subtitle: json['subtitle'],
      price: (json['price'] as num).toDouble(),
      rating: (json['rating'] as num).toDouble(),
      imageUrl: json['imageUrl'] ?? json['imageurl'] ?? '',
    );
  }
}

final List<String> categories = [
  'Cappuccino',
  'Machiato',
  'Latte',
  'Americano',
];
