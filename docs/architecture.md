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

---

## Rocky 0.3: Text Processing Engine

The text-processing engine lives in `rocky.language.text` and provides modular preprocessing independent of vocabulary management and the presentation layer:

1. **Normalization (`normalize_text`)**:
   * Trims whitespace and collapses repeated spaces, tabs, and newlines.
   * Separates punctuation that directly abuts word boundaries without breaking intra-word hyphens (`mangwanani-ngwanani`) or apostrophes (`nd'ani`).
   * Provides optional case normalization while preserving the original raw string.

2. **Tokenization (`tokenize`)**:
   * Extracts word tokens and distinct punctuation tokens using Unicode-compliant regex patterns.
   * Emits immutable `Token` dataclasses capturing `text`, `normalized`, `is_punctuation`, `start_char`, and `end_char`.
   * Preserves multi-character punctuation (e.g., ellipses `...`).

3. **Sentence Segmentation (`segment_sentences`)**:
   * Splits multi-sentence paragraphs on terminal punctuation (`.`, `!`, `?`).
   * Handles repeated punctuation sequences (e.g., `?!`, `...`) without emitting empty sentence fragments.

4. **Pipeline Orchestrator (`process_text` & `TextProcessor`)**:
   * Returns a structured `ProcessedText` object containing parsed `Sentence` and `Token` collections with document-level character offsets.

### Known Limitations of Rule-Based Segmentation
* **Abbreviations and Honorifics**: Titles (e.g. `Dr.`, `Prof.`) or abbreviations (e.g. `e.g.`, `i.e.`) containing periods may be incorrectly segmented as sentence endings.
* **Numbers with Decimals**: Decimal points (e.g. `3.14`) are preserved by lookaround assertions, but complex numerical notations or currency codes followed immediately by text may require future contextual refinement.
* **Dialogue Quotations**: Sentences ending in nested quotation marks following terminal punctuation are grouped with the preceding sentence.

---

## Rocky 0.4: Shona Linguistic Analysis

The linguistic analysis layer lives in `rocky.language.analysis` and provides extensible noun-class handling and morphological inspection:

1. **Separation of Linguistic Data and Analysis Logic**:
   * Data models (`NounClass`, `WordFormRelationship`, `MorphologicalRule`) and registries (`NounClassRegistry`, `RuleRegistry`) are decoupled from `ShonaLinguisticAnalyzer`.
   * Future grammatical rules and dialectal exceptions can be added via data registries without modifying analyzer source code.

2. **Certainty Levels & No Hallucinated Analysis**:
   * `CONFIRMED`: Word forms verified in documented lexical datasets.
   * `TENTATIVE`: General prefix-rule match with unverified stem or ambiguous noun class.
   * `UNRESOLVED`: Returned explicitly when no rule matches. The analyzer does not chop off arbitrary prefixes or invent root stems.

3. **Word-Form Relationships vs. Confirmed Morphological Decomposition**:
   * Storing that two words are related (e.g., `munhu` and `vanhu`) does not require claiming that all words follow identical agglutinative concatenation. Where decomposition has not been verified, `stem` is stored as `None`.

4. **Extending Noun Classes and Rules**:
   ```python
   from rocky.language import NounClass, NumberCategory, MorphologicalRule

   # Adding a noun class
   new_class = NounClass(
       identifier="1a",
       prefix="Ø",
       number=NumberCategory.SINGULAR,
       paired_class_id="2a",
       description="Kinship terms and proper names",
   )
   registry.register(new_class)

   # Adding a morphological rule
   new_rule = MorphologicalRule(
       rule_id="cl11_to_cl10_ru_dzi",
       description="Transform Class 11 ru- to Class 10 dzi-",
       source_prefix="ru",
       target_prefix="dzi",
       source_class_id="11",
       target_class_id="10",
   )
   rule_registry.register(new_rule)

---

## Rocky 0.5: Concord Agreement and Linguistic Validation

The concord agreement layer lives in `rocky.language.analysis` and models grammatical agreement (chivakashure chechirevo / chisazitasingwi) between controlling nouns and dependent syntactic elements:

1. **Separation of Agreement Categories**:
   * Agreement forms vary according to syntactic function. `ConcordCategory` distinguishes `SUBJECT`, `ADJECTIVE`, `POSSESSIVE`, and `OBJECT` agreements.
   * `ConcordRecord` models individual concord markers paired with bibliographical source documentation (e.g. Fortune 1984).

2. **Integration with Noun-Class Analysis**:
   * `ShonaConcordAnalyzer` consumes the noun-class outputs from `ShonaLinguisticAnalyzer` rather than re-parsing noun morphology.
   * Certainty levels are strictly maintained: confirmed nouns yield `CONFIRMED` concords, while ambiguous or derived nouns yield `TENTATIVE` concords marked with `is_ambiguous=True`. Unresolved nouns yield `UNRESOLVED` concords with explicit explanations.

3. **Syntactic Agreement Validation**:
   * `validate_agreement(noun, target, category)` evaluates whether an inflected verb or modifier satisfies agreement with the subject noun.
   * `validate_token_agreement` directly evaluates sequences of `Token` instances emitted by Rocky 0.3.

### Linguistic Assumptions and Validation Status
* **Grammatical Sources**: Concord markers are sourced from Fortune (1980/1984), Hannan (1984), and Dale (1972).
* **Phonological Coalescence**: Vowel-initial verb stems (e.g., `a-` + `-enda` -> `akaenda` / `anoenda`) require tense/aspect vowel coalescence rules that will be expanded in future verbal milestones.
* **Dialectal Variation**: Dialectal variations (e.g. Manyika, Karanga, Korekore) in honorific concords (such as Class 1a taking Class 2 `va-` honorific agreement) are documented in record notes.

---

## Rocky 0.6: Linguistic Knowledge and Validation

Rocky 0.6 introduces a controlled linguistic knowledge and validation layer in `rocky.language.analysis`:

1. **Explicit Provenance and Attestation (`LinguisticEvidence`)**:
   * All linguistic data records retain explicit evidence (`source_type`, `citation`, `attestation_status`, `dialect_scope`).
   * `AttestationStatus` requires explicit assignment (`VERIFIED`, `PROVISIONAL`, `CONTESTED`) with no default fallbacks.

2. **Refined Validation Classification (`ValidationVerdict`)**:
   * Replaces binary matching with six explicit states:
     * `CONFIRMED_MATCH`: Concord prefix matches and the stem is verified in the knowledge base.
     * `UNVERIFIED_STEM_MATCH`: Concord prefix matches, but the stem is unrecognized (distinguished from invalid forms).
     * `AMBIGUOUS_MATCH`: Matches one candidate interpretation of an ambiguous noun.
     * `CONCORD_MISMATCH`: Prefix present contradicts the controlling noun class.
     * `UNSUPPORTED_SYNTACTIC_FORM`: Target cannot yield a viable stem.
     * `UNRESOLVED_CONTROLLER`: Head noun has an unresolved noun class.

3. **Constrained Adjectival Mutation Rules**:
   * Initial consonant mutations in Classes 9 and 10 (*-kuru* $\rightarrow$ *huru*, *-tete* $\rightarrow$ *nhete*, *-refu* $\rightarrow$ *ndefu*, *-pamhi* $\rightarrow$ *mhamhi*, *-diki* $\rightarrow$ *ndiki*, *-chena* $\rightarrow$ *chena*) are supported with citations to Fortune (1984).

4. **Validation Guards and Category Scoping**:
   * **Mutation Guard**: In Classes 9 and 10, adjectives that require documented consonant mutation (e.g., *-kuru* -> *huru*) cannot bypass mutation via ordinary `i-` prefixation (*imba ikuru* evaluates to `CONCORD_MISMATCH`).
   * **Category Scoping**: Categories without formal stem validation engines (`POSSESSIVE`, `OBJECT`) explicitly return `UNSUPPORTED_SYNTACTIC_FORM` rather than falling through to verb validation.
   * **Diagnostic Conservatism**: Unverified residue (e.g., `munhu aporo`) is marked as `UNVERIFIED_STEM_MATCH`, and diagnostics explicitly clarify that prefix matching alone does not assert that the residue is a verb stem.