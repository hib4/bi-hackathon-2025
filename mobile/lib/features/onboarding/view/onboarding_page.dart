import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:kanca/features/auth/auth.dart';
import 'package:kanca/gen/assets.gen.dart';
import 'package:kanca/utils/utils.dart';

class OnboardingPage extends StatefulWidget {
  const OnboardingPage({super.key});

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  final PageController _pageController = PageController();
  int _currentIndex = 0;

  final List<_OnboardingData> _onboardingSections = [
    _OnboardingData(
      image: Assets.images.artboard.image(),
      title: RichText(
        textAlign: TextAlign.center,
        text: TextSpan(
          style: GoogleFonts.fredoka(
            fontSize: 32,
            fontWeight: FontWeight.w600,
            color: const Color(0XFF373737),
          ),
          children: const [
            TextSpan(text: 'Yuk, Mulai Petualangan '),
            TextSpan(
              text: 'Ceritamu!',
              style: TextStyle(
                color: Color(
                  0XFFFF9F00,
                ), // Use the same color as in the original code
              ),
            ),
          ],
        ),
      ),
      subtitle: const Text(
        'Di Kanca, kamu bisa buat cerita seru sendiri, belajar nilai baik & jadi jago atur uang, semuanya sambil main!',
        style: TextStyle(
          fontSize: 16,
          color: Colors.black,
        ),
        textAlign: TextAlign.center,
      ),
    ),
    _OnboardingData(
      image: Assets.images.artboard.image(), // Replace with actual image
      title:RichText(
        textAlign: TextAlign.center,
        text: TextSpan(
          style: GoogleFonts.fredoka(
            fontSize: 32,
            fontWeight: FontWeight.w600,
            color: const Color(0XFF373737),
          ),
          children: const [
            TextSpan(text: 'Pilih '),
            TextSpan(
              text: 'Jalan Ceritamu, ',
              style: TextStyle(
                color: Color(
                  0XFFFF9F00,
                ), // Use the same color as in the original code
              ),
            ),
            TextSpan(text: 'Petik Pelajarannya!'),
          ],
        ),
      ),
      subtitle: const Text(
        'Akhir cerita tergantung pilihanmu! Belajar menabung, jujur, dan bijak dengan cara yang seru & interaktif.',
        style: TextStyle(
          fontSize: 16,
          color: Colors.black,
        ),
        textAlign: TextAlign.center,
      ),
    ),
    _OnboardingData(
      image: Assets.images.artboard.image(), // Replace with actual image
      title: RichText(
        textAlign: TextAlign.center,
        text: TextSpan(
          style: GoogleFonts.fredoka(
            fontSize: 32,
            fontWeight: FontWeight.w600,
            color: const Color(0XFF373737),
          ),
          children: const [
            TextSpan(text: 'Ciptakan Momen, '),
            TextSpan(
              text: 'Bangun Nilai',
              style: TextStyle(
                color: Color(
                  0XFFFF9F00,
                ), // Use the same color as in the original code
              ),
            ),
          ],
        ),
      ),
      subtitle: const Text(
        'Bersama Kanca, belajar menjadi perjalanan berharga untuk masa depan anak yang bijak.',
        style: TextStyle(
          fontSize: 16,
          color: Colors.black,
        ),
        textAlign: TextAlign.center,
      ),
    ),
  ];

  void _onNext() {
    if (_currentIndex < _onboardingSections.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    } else {
      _finishOnboarding();
    }
  }

  void _onSkip() {
    _finishOnboarding();
  }

  void _finishOnboarding() {
    context.pushAndRemoveUntil(const LoginPage(), (route) => false);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0XFFFFF8E8),
      body: Stack(
        children: [
          // Background image
          Assets.images.artboard.image(
            fit: BoxFit.cover,
            width: double.infinity,
            height: double.infinity,
          ),
          PageView.builder(
            controller: _pageController,
            itemCount: _onboardingSections.length,
            onPageChanged: (index) {
              setState(() {
                _currentIndex = index;
              });
            },
            itemBuilder: (context, index) {
              final data = _onboardingSections[index];
              return Padding(
                padding: EdgeInsets.only(
                  top: MediaQuery.of(context).padding.top + 90,
                  left: 32,
                  right: 32,
                ),
                child: Column(
                  children: [
                    data.title,
                    16.vertical,
                    data.subtitle,
                  ],
                ),
              );
            },
          ),
          Visibility(
            visible: _currentIndex < _onboardingSections.length - 1,
            child: Positioned(
              top: 0,
              right: 0,
              child: Padding(
                padding: EdgeInsets.only(
                  left: 24,
                  right: 24,
                  top: MediaQuery.of(context).padding.top + 16,
                ),
                child: GestureDetector(
                  onTap: _onSkip,
                  child: const Text(
                    'Skip',
                    style: TextStyle(
                      fontSize: 20,
                      color: Color(0XFFFF9F00),
                    ),
                  ),
                ),
              ),
            ),
          ),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Padding(
              padding: const EdgeInsets.only(
                left: 24,
                right: 24,
                bottom: 32,
              ),
              child: Column(
                children: [
                  // indicator
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(_onboardingSections.length, (i) {
                      final isActive = i == _currentIndex;
                      return Container(
                        width: isActive ? 24 : 8,
                        height: 8,
                        margin: const EdgeInsets.only(right: 8),
                        decoration: BoxDecoration(
                          color: isActive
                              ? const Color(0XFFFF9F00)
                              : const Color(0XFFD9D9D9),
                          borderRadius: BorderRadius.circular(10),
                        ),
                      );
                    }),
                  ),
                  24.vertical,
                  ElevatedButton(
                    onPressed: _onNext,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0XFFFF9F00),
                      minimumSize: const Size(double.infinity, 56),
                    ),
                    child: Text(
                      _currentIndex == _onboardingSections.length - 1
                          ? 'Mulai'
                          : 'Lanjut',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _OnboardingData {
  const _OnboardingData({
    required this.image,
    required this.title,
    required this.subtitle,
  });

  final Widget image;
  final Widget title;
  final Widget subtitle;
}
