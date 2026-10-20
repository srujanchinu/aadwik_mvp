import 'package:flutter/material.dart';

import 'screens/home_screen.dart';

void main() {
  runApp(const AadwikApp());
}

class AadwikApp extends StatelessWidget {
  const AadwikApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Aadwik',
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.deepPurple,
        brightness: Brightness.dark,
      ),
      home: const HomeScreen(),
    );
  }
}