import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import '../widgets/error_retry.dart';

class NotificationPage extends StatelessWidget {
  const NotificationPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text('Notifications', style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color)),
        backgroundColor: Theme.of(context).appBarTheme.backgroundColor,
        elevation: 0,
        centerTitle: true,
      ),
      body: Consumer<AppProvider>(
        builder: (context, appProvider, child) {
          if (appProvider.notificationError != null) {
            return ErrorRetry(
              message: appProvider.notificationError!,
              onRetry: () => appProvider.fetchNotifications(),
            );
          }
          final notifications = appProvider.notifications;
          
          if (notifications.isEmpty) {
            return RefreshIndicator(
              onRefresh: () => appProvider.fetchNotifications(),
              child: ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: [
                  SizedBox(height: MediaQuery.of(context).size.height * 0.3),
                  const Center(
                    child: Column(
                      children: [
                        Icon(Icons.notifications_off_outlined, size: 80, color: Colors.grey),
                        SizedBox(height: 16),
                        Text('No notifications yet', style: TextStyle(fontSize: 18, color: Colors.grey)),
                      ],
                    ),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () => appProvider.fetchNotifications(),
            child: ListView.separated(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              itemCount: notifications.length,
              separatorBuilder: (context, index) => const SizedBox(height: 16),
              itemBuilder: (context, index) {
                final notification = notifications[index];
                
                // Map type to icon and color
                IconData icon = Icons.notifications;
                Color color = const Color(0xFFD4860B);
                
                if (notification.type == 'offer') {
                  icon = Icons.local_offer;
                  color = Colors.green;
                } else if (notification.type == 'reward') {
                  icon = Icons.star;
                  color = Colors.blue;
                } else if (notification.type == 'status') {
                  icon = Icons.local_cafe;
                  color = const Color(0xFFD4860B);
                }

                // Simple time formatter
                final difference = DateTime.now().difference(notification.createdAt);
                String timeText = '';
                if (difference.inMinutes < 60) {
                  timeText = '${difference.inMinutes}m ago';
                  if (difference.inMinutes == 0) timeText = 'Just now';
                } else if (difference.inHours < 24) {
                  timeText = '${difference.inHours}h ago';
                } else {
                  timeText = '${difference.inDays}d ago';
                }

                return GestureDetector(
                  onTap: () {
                    if (notification.isRead == 0) {
                      appProvider.markNotificationRead(notification.id);
                    }
                  },
                  child: _buildNotificationCard(
                    context: context,
                    icon: icon,
                    color: color,
                    title: notification.title,
                    time: timeText,
                    description: notification.description,
                    isNew: notification.isRead == 0,
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }

  Widget _buildNotificationCard({
    required BuildContext context,
    required IconData icon,
    required Color color,
    required String title,
    required String time,
    required String description,
    required bool isNew,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isNew ? color.withValues(alpha: Theme.of(context).brightness == Brightness.dark ? 0.2 : 0.05) : Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isNew ? color.withValues(alpha: 0.3) : (Theme.of(context).brightness == Brightness.dark ? Colors.grey[800]! : Colors.grey.shade200),
          width: 1,
        ),
        boxShadow: [
          if (!isNew)
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.03),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                        color: Theme.of(context).textTheme.bodyLarge?.color,
                      ),
                    ),
                    Text(
                      time,
                      style: TextStyle(
                        color: Colors.grey.shade500,
                        fontSize: 12,
                        fontWeight: isNew ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  description,
                  style: TextStyle(
                    color: Theme.of(context).brightness == Brightness.dark ? Colors.grey.shade400 : Colors.black54,
                    fontSize: 14,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
