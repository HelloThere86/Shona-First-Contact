# Rocky Architecture & Repository Layout

This document describes the design and boundaries established in **Rocky 0.01 — Foundation** and **Rocky 0.1 — Vocabulary Engine**.

## Directory Structure

* `src/rocky/`
  Root package directory using the standard `src/` layout.
  * `core/`: Common configuration, logging, constants, and shared base primitives.
  * `audio/`: Low-level audio recording, playback, feature extraction, and codec integration.
  * `language/`: Shona linguistic utilities, tokenizer hooks, morphosyntax rules, and vocabulary engine.
  * `translation/`: Alignment and translation orchestration.
  * `learning/`: Spaced repetition, user adaptation, and feedback mechanisms.
  * `ui/`: User interface components and presentation boundaries.

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
   * Employs atomic write operations (`tempfile` + `os.replace` + `os.fsync`) so an interrupted or failed write never corrupts an existing file.
   * Validates schema and catches malformed JSON with descriptive `StorageError` exceptions.

4. **`exceptions.py`**:
   * Defines explicit exception hierarchies (`VocabularyError`, `ValidationError`, `WordNotFoundError`, `DuplicateWordError`, `StorageError`).

### Linguistic Considerations & Known Limitations (0.1)
* **Single Primary Meaning**: Shona words frequently have multiple nuanced meanings depending on tone, noun class prefix, and context. Rocky 0.1 explicitly supports one primary English translation per Shona entry.
* **No Grammatical Analysis**: Rocky 0.1 does not perform morphological decomposition, agglutinative prefix analysis, or tone recognition. Those will be added in subsequent milestones.

### Usage Example

```python
from pathlib import Path
from rocky.language import VocabularyManager, WordNotFoundError

# 1. Initialize manager
vocab = VocabularyManager()

# 2. Add words
vocab.add("mvura", "water")
vocab.add("mukaka", "milk")
vocab.add("chikafu", "food")

# 3. Direct lookup
print(vocab.get_english("mvura"))  # -> "water"
print(vocab.get_shona("milk"))      # -> "mukaka"

# 4. Membership & update
if "chikafu" in vocab:
    vocab.update("chikafu", "nourishment")

# 5. Atomic persistence
vocab_path = Path("data/examples/my_vocab.json")
vocab.save_to_file(vocab_path)

# 6. Reloading
new_vocab = VocabularyManager()
new_vocab.load_from_file(vocab_path)
print(len(new_vocab))               # -> 3