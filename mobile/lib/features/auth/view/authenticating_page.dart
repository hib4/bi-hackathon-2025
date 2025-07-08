import 'package:flutter/material.dart';
import 'package:kanca/gen/assets.gen.dart';
import 'package:kanca/utils/utils.dart';

class AuthenticatingPage extends StatelessWidget {
  const AuthenticatingPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0XFFFFFAE5),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Assets.icons.kanca.image(
              width: 235,
              height: 235,
            ),
            const Text(
              'Kanca',
              style: TextStyle(
                fontSize: 40,
                fontWeight: FontWeight.w600,
                color: Color(0XFF1BB79E),
              ),
            ),
            8.vertical,
            const Text(
              'Teman cerita, teman belajar',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 16,
                color: Colors.black,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

