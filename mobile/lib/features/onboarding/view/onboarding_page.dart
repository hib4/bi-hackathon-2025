import 'package:flutter/material.dart';
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
      image: Assets.images.onboarding1.image(),
      title: RichText(
        textAlign: TextAlign.center,
        text: const TextSpan(
          style: TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.w600,
            color: Colors.black,
          ),
          children: [
            TextSpan(text: 'Hi! Selamat datang di '),
            TextSpan(
              text: 'Kanca!',
              style: TextStyle(
                color: Color(0XFF1BB79E),
              ),
            ),
          ],
        ),
      ),
      subtitle: const Text(
        'Teman cerita seru dan cerdas si kecil.',
        style: TextStyle(
          fontSize: 16,
          color: Colors.black,
        ),
        textAlign: TextAlign.center,
      ),
    ),
    _OnboardingData(
      image: Assets.images.onboarding1.image(), // Replace with actual image
      title: const Text(
        'Eksplorasi Cerita',
        style: TextStyle(
          fontSize: 32,
          fontWeight: FontWeight.w600,
          color: Colors.black,
        ),
        textAlign: TextAlign.center,
      ),
      subtitle: const Text(
        'Baca dan dengarkan cerita menarik yang edukatif.',
        style: TextStyle(
          fontSize: 16,
          color: Colors.black,
        ),
        textAlign: TextAlign.center,
      ),
    ),
    _OnboardingData(
      image: Assets.images.onboarding1.image(), // Replace with actual image
      title: const Text(
        'Belajar Sambil Bermain',
        style: TextStyle(
          fontSize: 32,
          fontWeight: FontWeight.w600,
          color: Colors.black,
        ),
        textAlign: TextAlign.center,
      ),
      subtitle: const Text(
        'Kembangkan imajinasi dan pengetahuan si kecil.',
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
      backgroundColor: const Color(0XFFFFFAE5),
      body: Stack(
        children: [
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
              return Column(
                children: [
                  data.image,
                  42.vertical,
                  data.title.withPadding(
                    left: 24,
                    right: 24,
                  ),
                  32.vertical,
                  data.subtitle.withPadding(
                    left: 24,
                    right: 24,
                  ),
                ],
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
                      color: Colors.black,
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
                              ? const Color(0XFF1BB79E)
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
                      backgroundColor: const Color(0XFF1BB79E),
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
