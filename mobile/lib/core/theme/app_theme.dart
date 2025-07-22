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
      50: const Color(0xFFFFF5E6),
      100: const Color(0xFFFFE1B0),
      200: const Color(0xFFFFD38A),
      300: const Color(0xFFFFBF54),
      400: const Color(0xFFFFB233),
      500: const Color(0xFFFF9F00),
      600: const Color(0xFFE89100),
      700: const Color(0xFFB57100),
      800: const Color(0xFF8C5700),
      900: const Color(0xFF6B4300),
    };

    // Secondary
    final secondary = {
      50: const Color(0xFFFFF1EF),
      100: const Color(0xFFFFD2CE),
      200: const Color(0xFFFFBDB6),
      300: const Color(0xFFFF9F95),
      400: const Color(0xFFFF8C81),
      500: const Color(0xFFFF6F61),
      600: const Color(0xFFE86558),
      700: const Color(0xFFB54F45),
      800: const Color(0xFF8C3D35),
      900: const Color(0xFF6B2F29),
    };

    // Support
    final support = {
      50: const Color(0xFFFFF7F8),
      100: const Color(0xFFFFE7EA),
      200: const Color(0xFFFFDCDF),
      300: const Color(0xFFFFCCD1),
      400: const Color(0xFFFFC2C8),
      500: const Color(0xFFFFB3BA),
      600: const Color(0xFFE8A3A9),
      700: const Color(0xFFB57F84),
      800: const Color(0xFF8C6266),
      900: const Color(0xFF6B4B4E),
    };

    // Dark Accent
    final darkAccent = {
      50: const Color(0xFFEBEAEF),
      100: const Color(0xFFC2BFCC),
      200: const Color(0xFFA49FB3),
      300: const Color(0xFF7A7490),
      400: const Color(0xFF61597B),
      500: const Color(0xFF392F5A),
      600: const Color(0xFF342B52),
      700: const Color(0xFF282140),
      800: const Color(0xFF1F1A32),
      900: const Color(0xFF181426),
    };

    // Neutral
    final neutral = {
      50: const Color(0xFFFFFEFD),
      100: const Color(0xFFFFFDF9),
      200: const Color(0xFFFFFCF7),
      300: const Color(0xFFFFFBF3),
      400: const Color(0xFFFFFAF1),
      500: const Color(0xFFFFF9ED),
      600: const Color(0xFFE8E3D8),
      700: const Color(0xFFB5B1A8),
      800: const Color(0xFF8C8982),
      900: const Color(0xFF6B6964),
    };

    // Grey
    final grey = {
      50: const Color(0xFFEBEBEB),
      100: const Color(0xFFC1C1C1),
      200: const Color(0xFFA3A3A3),
      300: const Color(0xFF797979),
      400: const Color(0xFF5F5F5F),
      500: const Color(0xFF373737),
      600: const Color(0xFF323232),
      700: const Color(0xFF272727),
      800: const Color(0xFF1E1E1E),
      900: const Color(0xFF171717),
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
    required this.lexendH1,
    required this.lexendH2,
    required this.lexendH3,
    required this.lexendH4,
    required this.lexendH5,
    required this.lexendLargeBody,
    required this.lexendBody,
    required this.lexendCaption,
    required this.lexendMicro,
  });

  factory AppTextStyles.textStyles() {
    return AppTextStyles(
      h1: GoogleFonts.fredoka(
        fontSize: 80,
        fontWeight: FontWeight.w600, // SemiBold
        height: 1.5,
        color: Colors.black,
      ),
      h2: GoogleFonts.fredoka(
        fontSize: 61,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
        color: Colors.black,
      ),
      h3: GoogleFonts.fredoka(
        fontSize: 47,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
        color: Colors.black,
      ),
      h4: GoogleFonts.fredoka(
        fontSize: 36,
        fontWeight: FontWeight.w600, // SemiBold
        height: 1.5,
        color: Colors.black,
      ),
      h5: GoogleFonts.fredoka(
        fontSize: 27,
        fontWeight: FontWeight.w500, // Medium
        height: 1.5,
        color: Colors.black,
      ),
      largeBody: GoogleFonts.fredoka(
        fontSize: 21,
        fontWeight: FontWeight.w600, // SemiBold
        height: 1.5,
        color: Colors.black,
      ),
      body: GoogleFonts.fredoka(
        fontSize: 16,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
        color: Colors.black,
      ),
      caption: GoogleFonts.fredoka(
        fontSize: 12,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
        color: Colors.black,
      ),
      micro: GoogleFonts.fredoka(
        fontSize: 9,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
        color: Colors.black,
      ),
      lexendH1: GoogleFonts.lexend(
        fontSize: 80,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
        color: Colors.black,
      ),
      lexendH2: GoogleFonts.lexend(
        fontSize: 61,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
        color: Colors.black,
      ),
      lexendH3: GoogleFonts.lexend(
        fontSize: 47,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
        color: Colors.black,
      ),
      lexendH4: GoogleFonts.lexend(
        fontSize: 36,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
        color: Colors.black,
      ),
      lexendH5: GoogleFonts.lexend(
        fontSize: 27,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
        color: Colors.black,
      ),
      lexendLargeBody: GoogleFonts.lexend(
        fontSize: 21,
        fontWeight: FontWeight.w600, // SemiBold
        height: 1.5,
        color: Colors.black,
      ),
      lexendBody: GoogleFonts.lexend(
        fontSize: 16,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
        color: Colors.black,
      ),
      lexendCaption: GoogleFonts.lexend(
        fontSize: 12,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
        color: Colors.black,
      ),
      lexendMicro: GoogleFonts.lexend(
        fontSize: 9,
        fontWeight: FontWeight.w400, // Regular
        height: 1.5,
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
  final TextStyle lexendH1;
  final TextStyle lexendH2;
  final TextStyle lexendH3;
  final TextStyle lexendH4;
  final TextStyle lexendH5;
  final TextStyle lexendLargeBody;
  final TextStyle lexendBody;
  final TextStyle lexendCaption;
  final TextStyle lexendMicro;
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
      scaffoldBackgroundColor: appColors.neutral[500],
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
