import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:http/http.dart' as http;
import 'package:kanca/core/core.dart';
import 'package:kanca/features/test_page.dart';
import 'package:kanca/gen/assets.gen.dart';
import 'package:kanca/utils/extensions/extensions.dart';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _isLoading = false;

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _goToLogin() {
    Navigator.of(context).pop();
  }

  Future<void> _register() async {
    setState(() => _isLoading = true);
    final name = _nameController.text.trim();
    final email = _emailController.text.trim();
    final password = _passwordController.text;

    try {
      final response = await http.post(
        Uri.parse(
          '${Env.apiBaseUrl}/register',
        ), // Replace with your actual API endpoint
        headers: {'Content-Type': 'application/json'},
        body: '{"name": "$name", "email": "$email", "password": "$password"}',
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        final token = data['token'] as String?;
        if (token != null) {
          // Save token to secure storage or state management
          await SecureStorageService().write('token', token);
          // Navigate to home page or dashboard
          if (mounted) {
            await context.push(const TestPage());
          }
        }
      } else {
        // Handle error
        final error = data['detail'] as String? ?? 'Unknown error';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Login failed: $error')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('An error occurred: $e')),
      );
    }
    setState(() => _isLoading = false);
  }

  Future<void> _registerWithGoogle() async {
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 1));
    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0XFFFFF8E8),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              48.vertical,
              Center(
                child: Assets.icons.kanca.image(
                  width: 90,
                  height: 90,
                ),
              ),
              32.vertical,
              RichText(
                textAlign: TextAlign.center,
                text: TextSpan(
                  style: GoogleFonts.fredoka(
                    fontSize: 32,
                    fontWeight: FontWeight.w600,
                    color: const Color(0XFF373737),
                  ),
                  children: const [
                    TextSpan(text: 'Buat Akun '),
                    TextSpan(
                      text: 'Kanca!',
                      style: TextStyle(color: Color(0XFFFF9F00)),
                    ),
                  ],
                ),
              ),
              12.vertical,
              Text(
                'Daftar untuk mulai petualangan seru bersama Kanca!',
                style: GoogleFonts.fredoka(
                  fontSize: 16,
                  color: Colors.black,
                ),
                textAlign: TextAlign.center,
              ),
              32.vertical,
              TextField(
                controller: _nameController,
                keyboardType: TextInputType.name,
                decoration: InputDecoration(
                  labelText: 'Nama Lengkap',
                  labelStyle: GoogleFonts.fredoka(color: Colors.black54),
                  filled: true,
                  fillColor: Colors.white.withOpacity(0.9),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide.none,
                  ),
                  prefixIcon: const Icon(
                    Icons.person_outline,
                    color: Color(0XFFFF9F00),
                  ),
                ),
              ),
              20.vertical,
              TextField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                decoration: InputDecoration(
                  labelText: 'Email',
                  labelStyle: GoogleFonts.fredoka(color: Colors.black54),
                  filled: true,
                  fillColor: Colors.white.withOpacity(0.9),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide.none,
                  ),
                  prefixIcon: const Icon(
                    Icons.email_outlined,
                    color: Color(0XFFFF9F00),
                  ),
                ),
              ),
              20.vertical,
              TextField(
                controller: _passwordController,
                obscureText: _obscurePassword,
                decoration: InputDecoration(
                  labelText: 'Password',
                  labelStyle: GoogleFonts.fredoka(color: Colors.black54),
                  filled: true,
                  fillColor: Colors.white.withOpacity(0.9),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide.none,
                  ),
                  prefixIcon: const Icon(
                    Icons.lock_outline,
                    color: Color(0XFFFF9F00),
                  ),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscurePassword
                          ? Icons.visibility_off
                          : Icons.visibility,
                      color: Colors.black38,
                    ),
                    onPressed: () {
                      setState(() {
                        _obscurePassword = !_obscurePassword;
                      });
                    },
                  ),
                ),
              ),
              20.vertical,
              TextField(
                controller: _confirmPasswordController,
                obscureText: _obscureConfirmPassword,
                decoration: InputDecoration(
                  labelText: 'Konfirmasi Password',
                  labelStyle: GoogleFonts.fredoka(color: Colors.black54),
                  filled: true,
                  fillColor: Colors.white.withOpacity(0.9),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide.none,
                  ),
                  prefixIcon: const Icon(
                    Icons.lock_outline,
                    color: Color(0XFFFF9F00),
                  ),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscureConfirmPassword
                          ? Icons.visibility_off
                          : Icons.visibility,
                      color: Colors.black38,
                    ),
                    onPressed: () {
                      setState(() {
                        _obscureConfirmPassword = !_obscureConfirmPassword;
                      });
                    },
                  ),
                ),
              ),
              32.vertical,
              SizedBox(
                height: 56,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _register,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0XFFFF9F00),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    textStyle: GoogleFonts.fredoka(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                    elevation: 0,
                  ),
                  child: _isLoading
                      ? const CircularProgressIndicator(
                          valueColor: AlwaysStoppedAnimation(Colors.white),
                        )
                      : const Text(
                          'Daftar',
                          style: TextStyle(color: Colors.white),
                        ),
                ),
              ),
              24.vertical,
              Row(
                children: [
                  const Expanded(child: Divider(thickness: 1)),
                  12.horizontal,
                  Text('atau', style: GoogleFonts.fredoka()),
                  12.horizontal,
                  const Expanded(child: Divider(thickness: 1)),
                ],
              ),
              24.vertical,
              SizedBox(
                height: 56,
                child: OutlinedButton.icon(
                  onPressed: _isLoading ? null : _registerWithGoogle,
                  icon: Assets.icons.google.svg(
                    width: 24,
                    height: 24,
                  ),
                  label: Text(
                    'Daftar dengan Google',
                    style: GoogleFonts.fredoka(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.black,
                    ),
                  ),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0XFFFF9F00)),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    backgroundColor: Colors.white.withOpacity(0.95),
                    elevation: 0,
                  ),
                ),
              ),
              32.vertical,
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    'Sudah punya akun?',
                    style: GoogleFonts.fredoka(color: Colors.black54),
                  ),
                  TextButton(
                    onPressed: _goToLogin,
                    style: TextButton.styleFrom(
                      foregroundColor: const Color(0XFFFF9F00),
                    ),
                    child: Text(
                      'Login',
                      style: GoogleFonts.fredoka(
                        color: const Color(0XFFFF9F00),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              24.vertical,
            ],
          ),
        ),
      ),
    );
  }
}
