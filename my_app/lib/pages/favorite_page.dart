import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import 'detail_page.dart';
import '../widgets/error_retry.dart';

class FavoritePage extends StatelessWidget {
  const FavoritePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text('Favorites', style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color)),
        backgroundColor: Theme.of(context).appBarTheme.backgroundColor,
        elevation: 0,
        iconTheme: Theme.of(context).iconTheme,
      ),
      body: Consumer<AppProvider>(
        builder: (context, appProvider, child) {
          if (appProvider.favoriteError != null) {
            return ErrorRetry(
              message: appProvider.favoriteError!,
              onRetry: () => appProvider.fetchFavorites(),
            );
          }
          final favorites = appProvider.favoriteCoffees;

          if (favorites.isEmpty) {
            return RefreshIndicator(
              onRefresh: () => appProvider.fetchFavorites(),
              child: ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: [
                  SizedBox(height: MediaQuery.of(context).size.height * 0.3),
                  Center(
                    child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.favorite_border, size: 80, color: Colors.grey.shade300),
                  const SizedBox(height: 16),
                  const Text(
                    'No favorites yet',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Like a coffee to save it here!',
                    style: TextStyle(fontSize: 14, color: Colors.grey),
                  ),
                ],
              ),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () => appProvider.fetchFavorites(),
            child: ListView.builder(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
            itemCount: favorites.length,
            itemBuilder: (context, index) {
              final coffee = favorites[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 16),
                elevation: 2,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                child: ListTile(
                  contentPadding: const EdgeInsets.all(12),
                  leading: ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Hero(
                      tag: 'coffee-${coffee.id}',
                      child: Image.network(coffee.imageUrl, width: 60, height: 60, fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) => Container(
                          width: 60, height: 60,
                          color: Theme.of(context).brightness == Brightness.dark ? Colors.grey[800] : const Color(0xFFF0F0F0),
                          child: const Icon(Icons.coffee, color: Colors.brown),
                        ),
                      ),
                    ),
                  ),
                  title: Text(coffee.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(coffee.subtitle),
                  trailing: IconButton(
                    icon: const Icon(Icons.favorite, color: Colors.red),
                    onPressed: () {
                      if (coffee.id != null) {
                        appProvider.toggleFavorite(coffee.id!);
                      }
                    },
                  ),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => CoffeeDetailPage(item: coffee)),
                    );
                  },
                ),
              );
            },
          ),
          );
        },
      ),
    );
  }
}
