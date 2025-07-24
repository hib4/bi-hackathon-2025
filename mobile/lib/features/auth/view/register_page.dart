import 'dart:convert';

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:http/http.dart' as http;
import 'package:kanca/core/core.dart';
import 'package:kanca/features/auth/view/login_page.dart';
import 'package:kanca/features/test_page.dart';
import 'package:kanca/gen/assets.gen.dart';
import 'package:kanca/utils/extensions/extensions.dart';
import 'package:kanca/widgets/widgets.dart';

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
    final colors = context.colors;
    final textTheme = context.textTheme;
    return Scaffold(
      backgroundColor: colors.primary[500],
      body: Stack(
        children: [
          Center(
            child: Column(
              children: [
                Expanded(
                  child: Center(
                    child: Text(
                      'DAFTAR',
                      style: textTheme.h1.copyWith(
                        color: Colors.white,
                        fontSize: 105,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 32,
                    ),
                    decoration: BoxDecoration(
                      color: colors.neutral[500],
                      borderRadius: const BorderRadius.vertical(
                        top: Radius.circular(24),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Email',
                          style: textTheme.caption,
                        ),
                        4.vertical,
                        KancaTextField(
                          controller: _emailController,
                          textInputType: TextInputType.emailAddress,
                          label: 'Email',
                        ),
                        16.vertical,
                        Text(
                          'Password',
                          style: textTheme.caption,
                        ),
                        4.vertical,
                        KancaTextField(
                          controller: _passwordController,
                          textInputType: TextInputType.visiblePassword,
                          label: 'Password',
                          isPassword: true,
                        ),
                        16.vertical,
                        Text(
                          'Konfirmasi Password',
                          style: textTheme.caption,
                        ),
                        4.vertical,
                        KancaTextField(
                          controller: _confirmPasswordController,
                          textInputType: TextInputType.visiblePassword,
                          label: 'Konfirmasi Password',
                          isPassword: true,
                        ),
                        32.vertical,
                        ElevatedButton(
                          onPressed: () {},
                          child: const Text('Mulai Sekarang'),
                        ),
                        // Or
                        16.vertical,
                        Row(
                          children: [
                            Expanded(
                              child: Divider(
                                color: Colors.black.withOpacity(0.4),
                                thickness: 1,
                              ),
                            ),
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                              ),
                              child: Text(
                                'Atau',
                                style: textTheme.caption,
                              ),
                            ),
                            Expanded(
                              child: Divider(
                                color: Colors.black.withOpacity(0.4),
                                thickness: 1,
                              ),
                            ),
                          ],
                        ),
                        24.vertical,
                        ElevatedButton(
                          onPressed: () {},
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.white,
                            foregroundColor: Colors.black,
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Assets.icons.google.svg(
                                width: 24,
                                height: 24,
                              ),
                              10.horizontal,
                              const Text('Lanjutkan dengan Google'),
                            ],
                          ),
                        ),
                        32.vertical,
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              'Sudah punya akun?',
                              style: textTheme.lexendCaption.copyWith(
                                fontSize: 14,
                              ),
                            ),
                            4.horizontal,
                            InkWell(
                              onTap: _goToLogin,
                              child: Text(
                                'Masuk!',
                                style: textTheme.lexendCaption.copyWith(
                                  color: colors.primary[500],
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const Spacer(),
                        Align(
                          alignment: Alignment.bottomCenter,
                          child: Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: RichText(
                              textAlign: TextAlign.center,
                              text: TextSpan(
                                style: textTheme.lexendCaption.copyWith(
                                  color: colors.grey[300],
                                  fontSize: 14,
                                ),
                                children: [
                                  const TextSpan(
                                    text:
                                        'Dengan menggunakan Kanca, Anda setuju pada ',
                                  ),
                                  TextSpan(
                                    text: 'Ketentuan Layanan',
                                    style: textTheme.lexendCaption.copyWith(
                                      fontWeight: FontWeight.w700,
                                      decoration: TextDecoration.underline,
                                      color: Colors.black,
                                    ),
                                    recognizer: TapGestureRecognizer()
                                      ..onTap = () {
                                        // TODO: Open Terms of Service link
                                      },
                                  ),
                                  const TextSpan(
                                    text: ' dan ',
                                  ),
                                  TextSpan(
                                    text: 'Kebijakan Privasi',
                                    style: textTheme.lexendCaption.copyWith(
                                      fontWeight: FontWeight.w700,
                                      decoration: TextDecoration.underline,
                                      color: Colors.black,
                                    ),
                                    recognizer: TapGestureRecognizer()
                                      ..onTap = () {
                                        // TODO: Open Privacy Policy link
                                      },
                                  ),
                                  const TextSpan(
                                    text: ' kami.',
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          Positioned(
            top: 145,
            left: 0,
            right: 0,
            child: Assets.mascots.auth.image(
              width: 200,
              height: 200,
            ),
          ),
        ],
      ),
    );
  }
}
