# Deck.GL Expressions Roadmap

This document outlines the roadmap for migrating Deck.GL layer properties from raw JavaScript string injection to a safe, declarative Mapbox GL JS-style expression language.

## Motivation
Previously, users could inject raw JavaScript functions (e.g., `getFillColor="d => [d.color[0], d.color[1], d.color[2], 255]"`) which were evaluated on the client using `eval()`. This poses an XSS security risk if data comes from untrusted sources.

To fix this, we have migrated to a declarative array-based expression format (e.g., `["get", "color"]`).

## Currently Supported Expressions
The following basic expressions have been implemented in `map_template.html`:

- `["get", propertyName]`: Retrieves the value of `propertyName` from the feature's properties or top-level data.
- `["has", propertyName]`: Checks if `propertyName` exists.
- `["literal", value]`: Returns the value as-is (prevents nested arrays from being evaluated as expressions).
- Arithmetic: `["+", a, b]`, `["-", a, b]`, `["*", a, b]`, `["/", a, b]`
- Comparisons: `["==", a, b]`, `["!=", a, b]`, `[">", a, b]`, `["<", a, b]`, `[">=", a, b]`, `["<=", a, b]`

These expressions are automatically applied as data accessors for any Deck.GL property if the array's first element matches a supported operator.

## Roadmap for Future Expressions

To achieve full feature parity with Mapbox/MapLibre GL JS expressions and eliminate the need for any complex JavaScript injection in Deck.GL layers, we need to implement the following expression types:

### 1. Advanced Data Access
- `["at", index, array]`: Retrieve an item from an array.
- `["length", string_or_array]`: Get the length of a string or array.
- `["in", keyword, input]`: Determine if a keyword exists in a string or array.

### 2. Control Flow & Interpolation
- `["match", input, label, output, ..., fallback]`: Select output based on matching an input to a set of labels.
- `["step", input, stop_output_0, stop_input_1, stop_output_1, ...]`: Produce discrete, stepped results.
- `["interpolate", interpolation, input, stop_input_0, stop_output_0, ...]`: Produce continuous, smooth results.
- `["case", condition, output, condition, output, ..., fallback]`: Select the first output whose corresponding condition evaluates to true.

### 3. Math Functions
- Advanced Math: `["abs", x]`, `["acos", x]`, `["asin", x]`, `["atan", x]`, `["ceil", x]`, `["cos", x]`, `["floor", x]`, `["ln", x]`, `["log10", x]`, `["log2", x]`, `["max", n, ...]`, `["min", n, ...]`, `["pi"]`, `["pow", x, y]`, `["round", x]`, `["sin", x]`, `["sqrt", x]`, `["tan", x]`.

### 4. String Operations
- `["concat", value, ...]`: Concatenate strings.
- `["downcase", string]`: Convert to lowercase.
- `["upcase", string]`: Convert to uppercase.

### 5. Color Operations
- `["rgba", r, g, b, a]`: Create an rgba color.
- `["to-rgba", color]`: Returns a four-element array containing the color's red, green, blue, and alpha components.

## Implementation Details

All evaluation logic is located in the `evaluateDeckExpression` JavaScript function in `maplibreum/templates/map_template.html`. As new expressions are added, they should be appended to this function. Future work may involve moving this logic to an external script or using an established lightweight expression parser if the complexity grows significantly.
