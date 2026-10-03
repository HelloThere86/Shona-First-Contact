# Rocky Architecture & Repository Layout

This document describes the design and boundaries established in the Rocky project.

## Directory Structure

* `src/rocky/`
  Root package directory using the standard `src/` layout.
  * `core/`: Common configuration, logging, constants, and shared base primitives.
  * `audio/`: Low-level audio recording, playback, feature extraction, and codec integration.
  * `language/`: Shona linguistic utilities, tokenizer hooks, morphosyntax rules, and vocabulary engine.
  * `translation/`: Alignment and translation orchestration.
  * `learning/`: Spaced repetition, user adaptation, and feedback mechanisms.
  * `ui/`: User interface components and presentation boundaries (CLI, menus, formatting).

* `data/`
  Data storage organized by processing lifecycle:
  * `raw/`: Unprocessed audio captures, transcripts, and source datasets (excluded from Git).
  * `processed/`: Cleaned, validated, and normalized data ready for modeling/lookup (excluded from Git).
  * `examples/`: Small, representative sample inputs and sample vocabulary files used for smoke tests and demonstrations.

* `tests/`
  Pytest suite containing unit and integration tests.

* `docs/`
  Architectural specifications, research notes, and setup guides.

* `experiments/`
  Exploratory prototypes and research scripts kept outside of production runtime code.

---

## Rocky 0.1: Vocabulary Engine Architecture

The vocabulary engine lives inside `rocky.language` and provides decoupled, modular vocabulary management:

1. **`VocabularyEntry` (`entry.py`)**:
   * Represents an immutable, normalized pairing between a Shona word and an English meaning.
   * Enforces type checks and whitespace stripping upon instantiation.
   * Provides `to_dict()` and `from_dict()` serialization hooks.

2. **`VocabularyManager` (`manager.py`)**:
   * Encapsulates all in-memory operations: adding, updating, removing, querying, and checking words.
   * Maintains O(1) primary lookups indexed by normalized Shona word.
   * Performs reverse English-to-Shona searches.
   * Implements Python container protocols (`len()`, `in`, `iter()`).

3. **`JsonVocabularyStorage` (`storage.py`)**:
   * Manages reading and writing data to JSON files.
   * Employs atomic write operations (`tempfile` + `os.replace` + `os.fsync`) so an interrupted write never corrupts an existing file.
   * Validates schema and catches malformed JSON with descriptive `StorageError` exceptions.

4. **`exceptions.py`**:
   * Defines explicit exception hierarchies (`VocabularyError`, `ValidationError`, `WordNotFoundError`, `DuplicateWordError`, `StorageError`).

---

## Rocky 0.2: Interactive Vocabulary CLI

The CLI lives inside `rocky.ui.cli` and acts as the presentation boundary for terminal interaction:

1. **Separation of Concerns**:
   * The CLI relies entirely on `VocabularyManager` for in-memory operations and `JsonVocabularyStorage` for persistence.
   * No business logic, collection filtering, or file serialization algorithms are implemented in `cli.py`.

2. **Testability via Inversion of Control**:
   * `VocabularyCLI` accepts injection of `input_func` and `output_func`.
   * Unit tests run completely headless without monkeypatching global terminal streams or blocking on manual input.

3. **Defensive Interaction Flow**:
   * Destructive actions (word deletion) require explicit confirmation.
   * File operations catch custom `StorageError` exceptions and display actionable user diagnostics rather than raw stack traces.