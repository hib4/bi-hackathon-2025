import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme extends InheritedWidget {
  const AppTheme({
    required this.textTheme,
    required this.colorTheme,
    required super.child,
    super.key,
  });

  final AppTextStyles textTheme;
  final AppColors colorTheme;

  // Static method to access the theme from context
  static AppTheme? of(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<AppTheme>();

  @override
  bool updateShouldNotify(covariant InheritedWidget oldWidget) => true;
}

/// Extension on BuildContext for easy theme access
extension ThemeExtension on BuildContext {
  AppTheme get themes {
    final theme = AppTheme.of(this);
    assert(theme != null, 'No AppTheme found in context');
    return theme!;
  }

  AppColors get colors {
    final theme = AppTheme.of(this);
    assert(theme != null, 'No AppTheme found in context');
    return theme!.colorTheme;
  }

  AppTextStyles get textTheme {
    final theme = AppTheme.of(this);
    assert(theme != null, 'No AppTheme found in context');
    return theme!.textTheme;
  }
}

///////////////////////////
///                     ///
///      COLORS         ///
///                     ///
///////////////////////////
class AppColors {
  const AppColors({
    required this.primary,
    required this.secondary,
    required this.support,
    required this.darkAccent,
    required this.neutral,
    required this.grey,
  });

  factory AppColors.colors() {
    // Primary
    final primary = {
      50: const Color(0xFFFFF8E8),
      100: const Color(0xFFFFE6A0),
      200: const Color(0xFFFFD36A),
      300: const Color(0xFFFFB800),
      400: const Color(0xFFFF9F00),
      500: const Color(0xFFFF8C00),
      600: const Color(0xFFC46A00),
      700: const Color(0xFF8C4B00),
      800: const Color(0xFF663600),
      900: const Color(0xFF402200),
    };

    // Secondary
    final secondary = {
      50: const Color(0xFFFFE6E6),
      100: const Color(0xFFFFB3B3),
      200: const Color(0xFFFF8C8C),
      300: const Color(0xFFFF6666),
      400: const Color(0xFFFF3D3D),
      500: const Color(0xFFE62E2E),
      600: const Color(0xFFB21F1F),
      700: const Color(0xFF8C1515),
      800: const Color(0xFF660D0D),
      900: const Color(0xFF400606),
    };

    // Support
    final support = {
      50: const Color(0xFFFFF0F5),
      100: const Color(0xFFFFD6E7),
      200: const Color(0xFFFFB3CF),
      300: const Color(0xFFFF8CB8),
      400: const Color(0xFFFF66A1),
      500: const Color(0xFFE64D8C),
      600: const Color(0xFFB23A6B),
      700: const Color(0xFF8C2C52),
      800: const Color(0xFF661F39),
      900: const Color(0xFF401226),
    };

    // Dark Accent
    final darkAccent = {
      50: const Color(0xFFE8E6F8),
      100: const Color(0xFFC6C1E7),
      200: const Color(0xFFA39DD6),
      300: const Color(0xFF8079C5),
      400: const Color(0xFF5D55B4),
      500: const Color(0xFF4B4291),
      600: const Color(0xFF3A326E),
      700: const Color(0xFF2C254B),
      800: const Color(0xFF1F1930),
      900: const Color(0xFF120D1A),
    };

    // Neutral
    final neutral = {
      50: const Color(0xFFFAFAFA),
      100: const Color(0xFFF5F5F5),
      200: const Color(0xFFF0F0F0),
      300: const Color(0xFFE0E0E0),
      400: const Color(0xFFD6D6D6),
      500: const Color(0xFFBDBDBD),
      600: const Color(0xFFA3A3A3),
      700: const Color(0xFF8A8A8A),
      800: const Color(0xFF707070),
      900: const Color(0xFF575757),
    };

    // Grey
    final grey = {
      50: const Color(0xFFF5F5F5),
      100: const Color(0xFFE0E0E0),
      200: const Color(0xFFCCCCCC),
      300: const Color(0xFFB3B3B3),
      400: const Color(0xFF999999),
      500: const Color(0xFF808080),
      600: const Color(0xFF666666),
      700: const Color(0xFF4D4D4D),
      800: const Color(0xFF333333),
      900: const Color(0xFF232323),
    };

    return AppColors(
      primary: primary,
      secondary: secondary,
      support: support,
      darkAccent: darkAccent,
      neutral: neutral,
      grey: grey,
    );
  }

  // Each color group is a map of shade to Color
  final Map<int, Color> primary;
  final Map<int, Color> secondary;
  final Map<int, Color> support;
  final Map<int, Color> darkAccent;
  final Map<int, Color> neutral;
  final Map<int, Color> grey;

  static AppColors of(BuildContext context) {
    final inheritedWidget = context
        .dependOnInheritedWidgetOfExactType<AppTheme>();
    assert(inheritedWidget != null, 'No AppTheme found in context');
    return inheritedWidget!.colorTheme;
  }
}

///////////////////////////
///     Text Style      ///
///////////////////////////
class AppTextStyles {
  AppTextStyles({
    required this.h1,
    required this.h2,
    required this.h3,
    required this.h4,
    required this.h5,
    required this.largeBody,
    required this.body,
    required this.caption,
    required this.micro,
  });

  factory AppTextStyles.textStyles() {
    return AppTextStyles(
      h1: GoogleFonts.fredoka(
        fontSize: 80,
        fontWeight: FontWeight.w600, // SemiBold
        height: 1,
        color: Colors.black,
      ),
      h2: GoogleFonts.fredoka(
        fontSize: 61,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
      h3: GoogleFonts.fredoka(
        fontSize: 47,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
      h4: GoogleFonts.fredoka(
        fontSize: 36,
        fontWeight: FontWeight.w600, // SemiBold
        height: 1,
        color: Colors.black,
      ),
      h5: GoogleFonts.fredoka(
        fontSize: 27,
        fontWeight: FontWeight.w500, // Medium
        height: 1,
        color: Colors.black,
      ),
      largeBody: GoogleFonts.fredoka(
        fontSize: 21,
        fontWeight: FontWeight.w600, // SemiBold
        height: 1,
        color: Colors.black,
      ),
      body: GoogleFonts.fredoka(
        fontSize: 16,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
      caption: GoogleFonts.fredoka(
        fontSize: 12,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
      micro: GoogleFonts.fredoka(
        fontSize: 9,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
    );
  }

  final TextStyle h1;
  final TextStyle h2;
  final TextStyle h3;
  final TextStyle h4;
  final TextStyle h5;
  final TextStyle largeBody;
  final TextStyle body;
  final TextStyle caption;
  final TextStyle micro;
}

///////////////////////////
///   Lexend TextStyle  ///
///////////////////////////
class AppLexendTextStyles {
  AppLexendTextStyles({
    required this.h1,
    required this.h2,
    required this.h3,
    required this.h4,
    required this.h5,
    required this.largeBody,
    required this.body,
    required this.caption,
    required this.micro,
  });

  factory AppLexendTextStyles.textStyles() {
    return AppLexendTextStyles(
      h1: GoogleFonts.lexend(
        fontSize: 80,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
      h2: GoogleFonts.lexend(
        fontSize: 61,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
      h3: GoogleFonts.lexend(
        fontSize: 47,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
      h4: GoogleFonts.lexend(
        fontSize: 36,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
      h5: GoogleFonts.lexend(
        fontSize: 27,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
      largeBody: GoogleFonts.lexend(
        fontSize: 21,
        fontWeight: FontWeight.w600, // SemiBold
        height: 1,
        color: Colors.black,
      ),
      body: GoogleFonts.lexend(
        fontSize: 16,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
      caption: GoogleFonts.lexend(
        fontSize: 12,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
      micro: GoogleFonts.lexend(
        fontSize: 9,
        fontWeight: FontWeight.w400, // Regular
        height: 1,
        color: Colors.black,
      ),
    );
  }

  final TextStyle h1;
  final TextStyle h2;
  final TextStyle h3;
  final TextStyle h4;
  final TextStyle h5;
  final TextStyle largeBody;
  final TextStyle body;
  final TextStyle caption;
  final TextStyle micro;
}

/// The theme data for this application.
/// Use this theme data for requiring style, such as AppBar, ElevatedButton, etc.
class AppThemeData {
  const AppThemeData({
    required this.themeData,
  });

  factory AppThemeData.themeData() {
    final appColors = AppColors.colors();
    final appTextStyles = AppTextStyles.textStyles();

    final primaryColor = appColors.primary[500] ?? const Color(0xFFFF8C00);
    final primaryColorMap = <int, Color>{
      50: primaryColor,
      100: primaryColor,
      200: primaryColor,
      300: primaryColor,
      400: primaryColor,
      500: primaryColor,
      600: primaryColor,
      700: primaryColor,
      800: primaryColor,
      900: primaryColor,
    };

    final primaryMaterialColor = MaterialColor(
      primaryColor.toARGB32(),
      primaryColorMap,
    );

    final themeData = ThemeData(
      useMaterial3: true,
      primaryColor: primaryColor,
      primarySwatch: primaryMaterialColor,
      colorScheme: ColorScheme.fromSwatch().copyWith(
        primary: appColors.primary.values.first,
        secondary: appColors.secondary.values.first,
      ),
      cupertinoOverrideTheme: const CupertinoThemeData(
        brightness: Brightness.light,
      ),
      scaffoldBackgroundColor: Colors.white,
      tabBarTheme: const TabBarThemeData(
        indicatorColor: Colors.black,
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: Colors.white,
      ),
      // actionIconTheme: ActionIconThemeData(
      //   backButtonIconBuilder: (context) => Assets.icons.arrowLeft.svg(),
      // ),
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.white,
        surfaceTintColor: appColors.neutral[100],
        elevation: 0,
        centerTitle: true,
        titleTextStyle: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
        iconTheme: const IconThemeData(
          color: Colors.white,
        ),
        actionsIconTheme: const IconThemeData(
          color: Colors.white,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 48),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          textStyle: GoogleFonts.lexend(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      textTheme: TextTheme(
        displayLarge: appTextStyles.h1,
        displayMedium: appTextStyles.h2,
        displaySmall: appTextStyles.h3,
        headlineLarge: appTextStyles.h4,
        headlineMedium: appTextStyles.h5,
        headlineSmall: appTextStyles.largeBody,
        bodyLarge: appTextStyles.body,
        bodyMedium: appTextStyles.caption,
        bodySmall: appTextStyles.micro,
      ),
    );

    return AppThemeData(
      themeData: themeData,
    );
  }

  final ThemeData? themeData;
}

void statusBarDarkStyle() {
  SystemChrome.setSystemUIOverlayStyle(systemUiOverlayDarkStyle);
}

SystemUiOverlayStyle get systemUiOverlayDarkStyle {
  return const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
    systemNavigationBarColor: Colors.white,
    systemNavigationBarIconBrightness: Brightness.dark,
  );
}

class NoOverScrollEffectBehavior extends ScrollBehavior {
  @override
  Widget buildOverscrollIndicator(
    BuildContext context,
    Widget child,
    ScrollableDetails details,
  ) {
    return child;
  }
}
