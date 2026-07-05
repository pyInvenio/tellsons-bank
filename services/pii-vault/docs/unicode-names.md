# Unicode Names

`MaskingService.maskName` trims the display name and returns the first UTF-16
code unit plus `***`. This is simple, but it means some unicode names may be
handled awkwardly when the first visible character is represented by multiple
code units.

Coverage should document current behavior for accented letters, combining
characters, emoji-like inputs, and whitespace. That gives reviewers evidence for
whether a future production change is needed.

Coverage priorities:

- accented names such as `Anais` with synthetic variants
- leading and trailing whitespace
- single-character names
- combining-mark edge cases
- null and blank input
