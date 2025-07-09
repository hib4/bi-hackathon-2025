import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:kanca/gen/assets.gen.dart';
import 'package:kanca/utils/utils.dart';

class AuthenticatingPage extends StatelessWidget {
  const AuthenticatingPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0XFFFFFFF8),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Assets.icons.kanca.image(
              width: 235,
              height: 235,
            ),
            24.vertical,
            Text(
              'Kanca',
              style: GoogleFonts.fredoka(
                fontSize: 40,
                fontWeight: FontWeight.bold,
                color: const Color(0XFFFF9F00),
              ),
            ),
            8.vertical,
            const Text(
              'Dari cerita jadi cuan!',
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
