import 'package:flutter/material.dart';

/// This extension adds two getters to the `double` class to easily create `SizedBox`
/// widgets with either a vertical or horizontal dimension equal to the value of the `double`.
extension XDouble on num {
  /// Returns a `SizedBox` widget with a height equal to the value of the `double`.
  Widget get vertical {
    return SizedBox(height: toDouble());
  }

  /// Returns a `SizedBox` widget with a width equal to the value of the `double`.
  Widget get horizontal {
    return SizedBox(width: toDouble());
  }
}

/// An extension on [BuildContext] that adds a method to show a [SnackBar] widget.
// extension BuildContextSnackBarExtension on BuildContext {
//   /// Shows a [SnackBar] widget with the given [message] and [duration].
//   ///
//   /// The default value for [duration] is 2 seconds.
//   void showSnackBar({
//     required String message,
//     Duration duration = const Duration(seconds: 2),
//   }) {
//     ScaffoldMessenger.of(this).showSnackBar(
//       SnackBar(
//         content: Text(
//           message,
//           style: textTheme.titleSmall,
//         ),
//         backgroundColor: colors.secondary,
//         duration: duration,
//       ),
//     );
//   }
// }

extension ContextExtension on BuildContext {
  void unFocusKeyboard() {
    FocusScope.of(this).unfocus();
  }
}

extension FunctionExtension<T> on T {
  Function get function => () {};
}

extension NavigatorContextExtension on BuildContext {
  /// Pushes a new page onto the navigator stack.
  Future<T?> push<T>(Widget page) {
    return Navigator.of(this).push<T>(
      MaterialPageRoute(builder: (_) => page),
    );
  }

  /// Replaces the current page with a new one.
  Future<T?> pushReplacement<T, TO>(Widget page, {TO? result}) {
    return Navigator.of(this).pushReplacement<T, TO>(
      MaterialPageRoute(builder: (_) => page),
      result: result,
    );
  }

  /// Pushes a new page and removes all previous pages until predicate returns true.
  Future<T?> pushAndRemoveUntil<T>(
    Widget page,
    bool Function(Route<dynamic>) predicate,
  ) {
    return Navigator.of(this).pushAndRemoveUntil<T>(
      MaterialPageRoute(builder: (_) => page),
      predicate,
    );
  }

  /// Pops the current page off the navigator stack.
  void pop<T extends Object?>([T? result]) {
    Navigator.of(this).pop<T>(result);
  }

  /// Attempts to pop the current page, if possible.
  Future<bool> maybePop<T extends Object?>([T? result]) {
    return Navigator.of(this).maybePop<T>(result);
  }

  /// Pops pages until the predicate returns true.
  void popUntil(bool Function(Route<dynamic>) predicate) {
    Navigator.of(this).popUntil(predicate);
  }
}
