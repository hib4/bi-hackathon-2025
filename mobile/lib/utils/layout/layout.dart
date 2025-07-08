import 'package:flutter/widgets.dart';

/// Extension on [Widget] to add padding and margin to a widget.
extension WidgetPaddingExtension on Widget {
  /// Adds padding to the widget.
  ///
  /// [left], [top], [right], [bottom] and [all] are optional parameters to specify the padding values.
  /// If [padding] is provided, it will be used instead of individual values.
  ///
  /// Returns a [Padding] widget with the specified padding and the original widget as its child.
  Widget withPadding({
    double? left,
    double? top,
    double? right,
    double? bottom,
    double? all,
    EdgeInsetsGeometry? padding,
  }) {
    final finalPadding = padding ??
        EdgeInsets.fromLTRB(
          left ?? all ?? 0.0,
          top ?? all ?? 0.0,
          right ?? all ?? 0.0,
          bottom ?? all ?? 0.0,
        );

    return Padding(
      padding: finalPadding,
      child: this,
    );
  }

  /// Adds margin to the widget.
  ///
  /// [left], [top], [right], [bottom] and [all] are optional parameters to specify the margin values.
  /// If [margin] is provided, it will be used instead of individual values.
  ///
  /// Returns a [Container] widget with the specified margin and the original widget as its child.
  Widget withMargin({
    double? left,
    double? top,
    double? right,
    double? bottom,
    double? all,
    EdgeInsetsGeometry? margin,
  }) {
    final finalMargin = margin ??
        EdgeInsets.fromLTRB(
          left ?? all ?? 0.0,
          top ?? all ?? 0.0,
          right ?? all ?? 0.0,
          bottom ?? all ?? 0.0,
        );

    return Container(
      margin: finalMargin,
      child: this,
    );
  }
}

/// Extension method to add a widget next to another widget in a row.
extension AddWidgetNextTo on Widget {
  /// Adds the given [widget] next to this widget in a row.
  Widget addNextTo(Widget widget) {
    return Row(
      children: <Widget>[this, widget],
    );
  }
}

extension StackWithFloatingButton on Widget {
  /// Adds a floating button at the bottom of the screen.
  ///
  /// The [button] parameter is the widget for the floating button,
  /// and [alignment] controls the alignment of the button within the stack.
  /// Default alignment is [Alignment.bottomCenter].
  Widget withFloatingButton(
    Widget button, {
    AlignmentGeometry alignment = Alignment.center,
  }) {
    return Stack(
      fit: StackFit.expand,
      children: [
        this,
        Positioned(
          bottom: 0,
          left: 0,
          right: 0,
          child: button,
        ),
      ],
    );
  }
}

/// Returns a centered value of type [T] for [CrossAxisAlignment],
/// [MainAxisAlignment], and [Alignment].
///
/// Throws an [UnsupportedError] if [T] is not one of the supported types.
///
/// Example usage on a Row:
/// ```
/// Row(
///   crossAxisAlignment: centered(),
///   mainAxisAlignment: centered(),
///   children: [
///     Container(),
///     Container(),
///   ],
/// )
/// ```
T centered<T>() {
  switch (T) {
    case CrossAxisAlignment:
      return CrossAxisAlignment.center as T;
    case MainAxisAlignment:
      return MainAxisAlignment.center as T;
    case Alignment:
      return Alignment.center as T;
    default:
      throw UnsupportedError('$T is not supported');
  }
}
