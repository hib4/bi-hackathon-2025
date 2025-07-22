import 'dart:convert';

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:kanca/core/core.dart';
import 'package:kanca/features/auth/auth.dart';
import 'package:kanca/features/test_page.dart';
import 'package:kanca/gen/assets.gen.dart';
import 'package:kanca/utils/extensions/extensions.dart';
import 'package:kanca/widgets/widgets.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;
  bool _isLoading = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    setState(() => _isLoading = true);
    final email = _emailController.text.trim();
    final password = _passwordController.text;

    try {
      final response = await http.post(
        Uri.parse(
          '${Env.apiBaseUrl}/login',
        ), // Replace with your actual API endpoint
        headers: {'Content-Type': 'application/json'},
        body: '{"email": "$email", "password": "$password"}',
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

  Future<void> _loginWithGoogle() async {
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 1));
    setState(() => _isLoading = false);
  }

  void _goToRegister() {
    context.push(const RegisterPage());
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
                  flex: 2,
                  child: Center(
                    child: Text(
                      'MASUK',
                      style: textTheme.h1.copyWith(
                        color: Colors.white,
                        fontSize: 105,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
                Expanded(
                  flex: 3,
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
                        12.vertical,
                        Align(
                          alignment: Alignment.centerRight,
                          child: InkWell(
                            onTap: () {},
                            child: Text(
                              'Forgot Password?',
                              style: textTheme.lexendCaption.copyWith(
                                color: colors.primary[500],
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                        32.vertical,
                        ElevatedButton(
                          onPressed: () {},
                          child: const Text('Lanjutkan'),
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
                              'Belum punya akun?',
                              style: textTheme.caption.copyWith(
                                fontSize: 14,
                              ),
                            ),
                            4.horizontal,
                            InkWell(
                              onTap: _goToRegister,
                              child: Text(
                                'Daftar sekarang!',
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
            top: 205,
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
