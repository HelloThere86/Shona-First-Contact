# Rocky Architecture & Repository Layout

This document describes the high-level layout established in **Rocky 0.01 — Foundation**.

## Directory Structure

* `src/rocky/`
  Root package directory using the standard `src/` layout.
  * `core/`: Common configuration, logging, constants, and shared base interfaces.
  * `audio/`: Low-level audio recording, playback, feature extraction, and codec integration.
  * `language/`: Shona linguistic utilities, tokenizer hooks, morphosyntax rules, and dictionaries.
  * `translation/`: Alignment and translation orchestration.
  * `learning/`: Spaced repetition, user adaptation, and feedback mechanisms.
  * `ui/`: User interface components and presentation boundaries.

* `data/`
  Data storage organized by processing lifecycle:
  * `raw/`: Unprocessed audio captures, transcripts, and source datasets (excluded from Git).
  * `processed/`: Cleaned, validated, and normalized data ready for modeling/lookup (excluded from Git).
  * `examples/`: Small, representative sample inputs used for smoke tests and documentation.

* `tests/`
  Pytest suite containing unit and integration tests covering packages in `src/rocky/`.

* `docs/`
  Architectural specifications, research notes, and setup guides.

* `experiments/`
  Exploratory prototypes and exploratory research scripts kept outside of production runtime code.