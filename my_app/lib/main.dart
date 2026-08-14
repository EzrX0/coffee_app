import 'package:flutter/material.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:provider/provider.dart';
import 'pages/onboarding_page.dart';
import 'pages/auth_page.dart';
import 'pages/home_page.dart';
import 'providers/app_provider.dart';
import 'providers/auth_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  Stripe.publishableKey = 'pk_test_51Tp13uRKk1FSnRdUZmnhVe5yi2WguKYS2pPG1wGkpO3CVnCKTiIBW56HBe2EgvmF7iE3LM0aRRxdpzlC3U8CvcjY00Ai4x5CRo';
  await Stripe.instance.applySettings();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()..initAuth()),
        ChangeNotifierProxyProvider<AuthProvider, AppProvider>(
          create: (_) => AppProvider(),
          update: (_, auth, app) => app!..updateToken(auth.token),
        ),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Coffee App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      home: const AuthWrapper(),
    );
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, auth, _) {
        if (auth.isAuthenticated) {
          return const CoffeeHomePage();
        }
        return const CoffeeOnboardingPage();
      },
    );
  }
}