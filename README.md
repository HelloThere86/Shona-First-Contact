# SHONA-FIRST-CONTACT

### An experimental language-learning and translation system inspired by *Project Hail Mary*

> *What happens when a computer encounters a language it does not understand?*

**Shona-First-Contact** is an experimental software project exploring how a computer can learn, represent, and translate the Shona language through progressively more sophisticated language-processing techniques.

The project is inspired by the communication and translation problem presented in Andy Weir's *Project Hail Mary*, particularly the process of establishing communication with Rocky.

This is **not** an attempt to recreate the fictional technology from the novel or film. Instead, it uses the fictional scenario as inspiration for building a real, progressively evolving language-learning system.

The "alien language" for this experiment is **Shona**.

---

## Project Vision

The long-term goal is to build a system capable of:

1. Receiving Shona text and eventually speech.
2. Identifying linguistic patterns.
3. Building an internal representation of words and phrases.
4. Learning relationships between Shona and English.
5. Using context to improve interpretation.
6. Allowing a human operator to teach and correct the system.
7. Maintaining what it has learned.
8. Eventually supporting real-time speech-based communication.

The system should evolve from a simple rule-based prototype into increasingly sophisticated language-processing and machine-learning components.

The important principle is:

> **Do not build the final system first. Build the system that can eventually become the final system.**

---

# Development Philosophy

Shona-First-Contact is intentionally being developed incrementally.

Each version should introduce a meaningful capability while keeping the previous functionality understandable and testable.

The project is also intended to serve as a practical software-engineering laboratory.

Development will therefore emphasize:

* Python
* Object-oriented programming
* Data structures and algorithms
* Clean architecture
* Git and version control
* Automated testing
* Documentation
* Debugging
* NLP
* Machine learning
* Speech processing
* UI/UX engineering
* System design

AI coding agents may be used during development.

However:

> **The AI may write code. The developer must understand what gets merged.**

Generated code should be reviewed, tested, understood, and integrated deliberately rather than blindly accepted.

---

# Current Development Roadmap

## Rocky 0.01 — Foundation

Establish the project itself.

* Repository initialization
* Project structure
* Git workflow
* Python environment
* Configuration management
* Basic test framework
* Initial documentation

---

## Rocky 0.1 — Vocabulary

Create the first language-learning engine.

The system should be capable of storing relationships such as:

```text
mvura → water
mukaka → milk
chikafu → food
```

The vocabulary system should support:

* Adding words
* Looking up words
* Removing words
* Updating meanings
* Saving vocabulary
* Loading vocabulary
* Basic validation

---

## Rocky 0.2 — Phrase Learning

Move beyond individual words.

Example:

```text
Huya nemvura.

→ Come with water.
```

The system begins examining relationships between words and their surrounding context.

---

## Rocky 0.3 — Sentence Analysis

Introduce:

* Tokenization
* Sentence segmentation
* Word frequency
* Pattern detection
* Basic grammatical relationships
* Context handling

The goal is to begin moving from:

```text
WORD → WORD
```

toward:

```text
SENTENCE → MEANING
```

---

## Rocky 0.4 — Learning Engine

Introduce a more sophisticated learning mechanism.

The system should be able to learn from examples rather than relying exclusively on manually created translation rules.

Example training data:

```text
Ndiri kunwa mvura.
I am drinking water.

Ndiri kunwa mukaka.
I am drinking milk.

Ndiri kudya sadza.
I am eating sadza.
```

The system should attempt to identify recurring structures and relationships.

---

## Rocky 0.5 — Human Teaching

Introduce an interactive teaching mechanism.

Example:

```text
UNKNOWN TERM

"mangwanani"

Possible interpretation:
[ unknown ]

Operator input:
Good morning
```

The system records the interaction as new knowledge.

The operator should be able to:

* Confirm interpretations
* Correct interpretations
* Add vocabulary
* Review learned knowledge
* Remove incorrect knowledge
* Inspect why a translation was produced

---

## Rocky 0.6 — Audio

Introduce speech input.

```text
MICROPHONE
    ↓
AUDIO PROCESSING
    ↓
SPEECH RECOGNITION
    ↓
SHONA TEXT
    ↓
LANGUAGE ENGINE
```

The initial objective is reliable conversion of spoken Shona into text.

---

## Rocky 0.7 — Translation

Introduce the complete translation pipeline.

```text
SHONA
  ↓
LANGUAGE PROCESSING
  ↓
MEANING REPRESENTATION
  ↓
ENGLISH
```

The system should expose confidence and uncertainty rather than pretending that every interpretation is correct.

---

## Rocky 0.8 — Conversation

Support two-way interaction:

```text
Human
 ↓
Shona
 ↓
Rocky
 ↓
English
```

and:

```text
English
 ↓
Rocky
 ↓
Shona
 ↓
Human
```

---

## Rocky 0.9 — Real-Time Communication

Combine:

* Microphone input
* Speech recognition
* Language processing
* Translation
* Text-to-speech
* Conversation history

The objective is a functioning real-time communication prototype.

---

# Rocky 1.0

The first complete version of the system.

Target capabilities:

* Text input
* Speech input
* Shona language processing
* English translation
* Human-assisted learning
* Persistent knowledge
* Conversation history
* Confidence estimation
* Error correction
* Real-time interaction
* Scientific-style interface

Future versions may move toward neural language models and more advanced learning techniques.

---

# Interface Design

The interface is a major part of the project.

It should feel like a **scientific communication system**, not a generic modern AI application.

### Design principles

The interface should:

* Avoid emojis.
* Avoid generic AI imagery.
* Avoid chatbot-style layouts where possible.
* Avoid excessive rounded cards.
* Avoid purple AI gradients.
* Avoid "AI assistant" visual clichés.
* Avoid unnecessary animations.
* Prioritize information density and readability.
* Use restrained typography.
* Use purposeful animation.
* Feel technological without becoming visually chaotic.

The visual inspiration is:

* Deep-space instrumentation
* Scientific research systems
* Spacecraft computers
* Early computer terminals
* Alien communication equipment
* Radar and telemetry interfaces
* Retro-futurism
* Mission-control systems

---

# Theme System

The application will support multiple visual themes.

## Terminal

A retro computer-terminal aesthetic.

```text
BLACK
+
TERMINAL GREEN
```

Inspired by early computer terminals and scientific instrumentation.

---

## Deep Space

A dark spacecraft/scientific interface.

```text
DEEP BLUE
+
BLACK
+
WHITE
```

The interface should feel like operating a computer aboard a spacecraft.

---

## Blackhole

A custom high-contrast theme inspired by a black hole and its event horizon.

Primary environment:

```text
DEEP BLACK
```

Accent system inspired by:

```text
EVENT HORIZON
ACCRETION DISK
THERMAL LIGHT
STELLAR PLASMA
```

The palette should use restrained luminous accents rather than turning the interface into a neon gaming UI.

The objective is:

> **Deep black space with the subtle visual presence of an event horizon.**

Themes should be switchable without changing application functionality.

---

# Proposed Interface

The primary interface will eventually contain several functional regions.

```text
┌──────────────────────────────────────────────────────────────┐
│ SHONA-FIRST-CONTACT                         SYSTEM: ONLINE   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  INPUT                         INTERPRETATION                │
│                                                              │
│  SHONA                         ENGLISH                       │
│  ───────────────               ───────────────               │
│  Huya nemvura.                 Come with water.              │
│                                                              │
│                                                              │
│  AUDIO STATUS                  CONFIDENCE                    │
│  ────────────                  ──────────                    │
│  SIGNAL DETECTED               94%                           │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ VOCABULARY │ LEARNING │ HISTORY │ SYSTEM │ THEME            │
└──────────────────────────────────────────────────────────────┘
```

The exact interface will evolve alongside the underlying system.

---

# Architecture

The project will use a modular architecture so individual components can evolve independently.

```text
shona-first-contact/
│
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── pyproject.toml
│
├── src/
│   ├── audio/
│   ├── language/
│   ├── translation/
│   ├── learning/
│   ├── ui/
│   └── core/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── examples/
│
├── tests/
│
├── docs/
│
└── experiments/
```

Components should communicate through clearly defined interfaces rather than becoming tightly coupled.

---

# Data

The project will distinguish between:

### Raw Data

Original datasets that should not be modified directly.

```text
data/raw/
```

### Processed Data

Cleaned and transformed datasets.

```text
data/processed/
```

### Examples

Small datasets used for development and testing.

```text
data/examples/
```

Sensitive or copyrighted datasets should not be committed to the repository unless their licensing explicitly permits redistribution.

---

# Testing

Testing is part of development rather than something added afterward.

Tests should eventually cover:

* Vocabulary management
* Text processing
* Sentence analysis
* Translation
* Learning behaviour
* Data persistence
* Audio processing
* UI logic
* Error handling

Tests should be run before merging significant changes.

---

# Version Control

Git is a core component of the project.

The `main` branch should represent a stable version of the application.

Development should occur through feature branches.

Example:

```text
main
│
├── feature/vocabulary
├── feature/text-processing
├── feature/learning-engine
├── feature/audio-input
├── feature/translation
└── feature/interface
```

A typical workflow:

```text
ISSUE
  ↓
FEATURE BRANCH
  ↓
IMPLEMENTATION
  ↓
TEST
  ↓
COMMIT
  ↓
REVIEW
  ↓
MERGE
```

Commit messages should describe the actual change.

Example:

```text
feat: add vocabulary storage
fix: handle empty translation input
test: add vocabulary lookup tests
refactor: separate translation logic from UI
docs: update learning engine architecture
```

---

# Project Principles

### 1. Build incrementally

Every version should work before the next major capability is added.

### 2. Understand the system

Complexity should not be hidden behind libraries or AI-generated code.

### 3. Measure before optimizing

Do not optimize components without understanding their behaviour.

### 4. Preserve uncertainty

If the system does not know something, it should be capable of saying so.

### 5. Human feedback is data

Corrections and teaching interactions should become useful training information.

### 6. Keep the architecture replaceable

Early implementations may eventually be replaced by better models or algorithms.

The interfaces between components should make that possible.

### 7. Experiment

Some components will be deliberately experimental.

Experiments belong in:

```text
experiments/
```

rather than silently becoming production architecture.

---

# Long-Term Research Questions

The project may eventually explore questions such as:

* How much language structure can be learned from limited examples?
* How can context disambiguate words with multiple meanings?
* How should uncertainty be represented?
* Can linguistic structure be learned without a large pretrained model?
* How can human corrections improve the system?
* How much Shona speech data is required for useful speech recognition?
* How can translation work when training data is limited?
* What happens when the system encounters previously unseen vocabulary?
* How should the system distinguish between a word it does not know and a word it has misunderstood?

These questions are part of the reason the project exists.

---

# Status

**Current version:** Rocky 0.01 — Foundation

**Status:** In development

**Primary language:** Python

**Project type:** Experimental NLP / AI / Software Engineering

---

# Disclaimer

Shona-First-Contact is an independent experimental project inspired by *Project Hail Mary*.

It is not affiliated with Andy Weir, the film adaptation, or any associated production company.

The project uses Shona as the experimental language because it provides a real-world language for experimentation without requiring the developer to invent and maintain an artificial language.

---

# The Mission

Start with:

```text
"mvura" → "water"
```

and see how far we can take it.

**First contact begins here.**

---

##### Update: `README.md`
Update the Roadmap section to reflect that Milestone 0.1 is complete:

```markdown
## Roadmap

- [x] **Rocky 0.01 — Foundation**: Package structure, pytest configuration, src/ layout.
- [x] **Rocky 0.1 — Vocabulary Engine**: Shona-English vocabulary management, entry validation, bidirectional lookup, atomic JSON persistence.
- [ ] **Rocky 0.2 — Lexical Analysis & Morphology**: Shona noun classes, prefixes, and tokenization.
- [ ] **Rocky 0.3 — Audio Engine & Phonetics**: Audio capture, playback, and phonetic representation.
- [ ] **Rocky 0.4 — Interactive Tutor & Memory**: Spaced repetition and adaptive learning loop.
- [ ] **Rocky 0.5 — Graphical User Interface**: Desktop application interface.