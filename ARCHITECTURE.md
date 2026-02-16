# AI Study Assistant - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STUDENT INTERFACE                                │
│                      (Streamlit Web Application)                         │
│                        src/ui/streamlit_app.py                          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      STUDY ASSISTANT CORE                                │
│                   src/services/study_assistant.py                       │
│  • Orchestrates all components                                          │
│  • Manages session state                                                │
│  • Coordinates design patterns                                          │
└──┬──────────┬──────────┬────────────┬─────────────┬────────────────────┘
   │          │          │            │             │
   ▼          ▼          ▼            ▼             ▼
┌──────┐ ┌──────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐
│Chain │ │Factory│ │Strategy  │ │Observer  │ │Configuration│
│of    │ │Pattern│ │Pattern   │ │Pattern   │ │Singleton    │
│Resp. │ │       │ │          │ │          │ │             │
└──┬───┘ └──┬───┘ └────┬─────┘ └────┬─────┘ └──────┬──────┘
   │        │          │            │               │
   │        │          │            │               │
   ▼        ▼          ▼            ▼               ▼

┌─────────────────────────────────────────────────────────────────────────┐
│                    CHAIN OF RESPONSIBILITY                               │
│           src/patterns/chain_of_responsibility.py                       │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │ Greeting │ -> │   Help   │ -> │  Direct  │ -> │   Hint   │ ->      │
│  │ Handler  │    │ Handler  │    │  Answer  │    │ Handler  │         │
│  └──────────┘    └──────────┘    │ Detector │    └──────────┘         │
│                                   └──────────┘                          │
│                                        │                                │
│                                        ▼                                │
│                              ┌──────────────────┐                       │
│                              │    Learning      │                       │
│                              │ Question Handler │                       │
│                              └──────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        FACTORY PATTERN                                   │
│                    src/patterns/factory.py                              │
├─────────────────────────────────────────────────────────────────────────┤
│  Question Input                                                          │
│       │                                                                  │
│       ▼                                                                  │
│  ┌─────────────────┐                                                    │
│  │ Question Type   │                                                    │
│  │   Detection     │                                                    │
│  └────────┬────────┘                                                    │
│           │                                                              │
│           ├─────────┬─────────┬──────────┬───────────┐                 │
│           ▼         ▼         ▼          ▼           ▼                 │
│      Conceptual  Problem   How-to      Why      Comparison             │
│           │         │         │          │           │                 │
│           └─────────┴─────────┴──────────┴───────────┘                 │
│                              │                                          │
│                              ▼                                          │
│                    Create Appropriate                                   │
│                     Strategy Instance                                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        STRATEGY PATTERN                                  │
│                 src/strategies/learning_strategies.py                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐               │
│  │   Socratic   │   │  Hint-Based  │   │  Conceptual  │               │
│  │   Strategy   │   │   Strategy   │   │   Strategy   │               │
│  │              │   │              │   │              │               │
│  │ • Questions  │   │ • Level 1-3  │   │ • Explain    │               │
│  │ • Guide      │   │ • Progressive│   │ • Principles │               │
│  │ • Discover   │   │ • No spoilers│   │ • Examples   │               │
│  └──────────────┘   └──────────────┘   └──────────────┘               │
│                                                                          │
│  ┌──────────────┐                                                       │
│  │   Problem    │   ← All implement LearningStrategy interface         │
│  │ Decomposition│                                                       │
│  │              │                                                       │
│  │ • Break down │                                                       │
│  │ • Steps      │                                                       │
│  │ • Methodology│                                                       │
│  └──────────────┘                                                       │
│                                                                          │
│  Strategy Context allows runtime switching between strategies           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        OBSERVER PATTERN                                  │
│                    src/patterns/observer.py                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│          ┌─────────────────────────────┐                                │
│          │  StudentProgressTracker     │                                │
│          │       (Subject)             │                                │
│          └────────┬────────────────────┘                                │
│                   │                                                      │
│         notify() all observers                                          │
│                   │                                                      │
│       ┌───────────┼───────────┬────────────┐                           │
│       │           │           │            │                           │
│       ▼           ▼           ▼            ▼                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                      │
│  │Progress │ │ Console │ │Analytics│ │  Custom │                      │
│  │ Logger  │ │ Tracker │ │ Tracker │ │Observer │                      │
│  │         │ │         │ │         │ │         │                      │
│  │ • JSON  │ │ • Print │ │ • Stats │ │ • Your  │                      │
│  │ • Files │ │ • Debug │ │ • Metrics│ │   Logic │                      │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘                      │
│                                                                          │
│  All observers receive updates when events occur                        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        SINGLETON PATTERN                                 │
│                    src/patterns/singleton.py                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│               ┌─────────────────────────────┐                           │
│               │    ConfigManager            │                           │
│               │    (Single Instance)        │                           │
│               ├─────────────────────────────┤                           │
│               │ • OLLAMA settings           │                           │
│               │ • App configuration         │                           │
│               │ • Database settings         │                           │
│               │ • UI preferences            │                           │
│               │ • Learning parameters       │                           │
│               └──────────┬──────────────────┘                           │
│                          │                                               │
│                  Accessed globally as                                    │
│                    'config' instance                                     │
│                          │                                               │
│         ┌────────────────┼────────────────┐                             │
│         ▼                ▼                ▼                             │
│    All Services    All Patterns    All Strategies                       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        OLLAMA INTEGRATION                                │
│                   src/services/ollama_service.py                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────┐              │
│  │              OllamaService                            │              │
│  ├──────────────────────────────────────────────────────┤              │
│  │  • generate_response(prompt, system_msg)             │              │
│  │  • is_available()                                    │              │
│  │  • list_models()                                     │              │
│  │  • chat(messages)                                    │              │
│  └──────────────────┬───────────────────────────────────┘              │
│                     │                                                   │
│                     │ HTTP Requests                                     │
│                     ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐               │
│  │         OLLAMA Server (localhost:11434)             │               │
│  │                                                      │               │
│  │  ┌────────────────┐                                 │               │
│  │  │   phi3:mini    │  ← AI Model (3.8GB)            │               │
│  │  │       or       │                                 │               │
│  │  │ llama3.2:1b    │  ← Alternative (1.3GB)          │               │
│  │  └────────────────┘                                 │               │
│  │                                                      │               │
│  │  Generates learning-focused responses                │               │
│  └─────────────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW                                         │
└─────────────────────────────────────────────────────────────────────────┘

Student Question
       │
       ▼
[Chain of Responsibility] → Special handling? → Return response
       │                          │
       │ No                       │ Yes
       ▼                          ▼
[Factory Pattern] ────────────────┘
       │
       ├─ Detect question type
       └─ Create strategy
              │
              ▼
[Strategy Pattern]
       │
       ├─ Generate learning prompt
       └─ Apply teaching approach
              │
              ▼
[OLLAMA Service]
       │
       ├─ Send to AI model
       └─ Get response
              │
              ▼
[Observer Pattern]
       │
       ├─ Log event
       ├─ Track progress
       └─ Update analytics
              │
              ▼
Return to Student
       │
       └─ Display with metadata
              (strategy, hints, etc.)

┌─────────────────────────────────────────────────────────────────────────┐
│                    EXTENSIBILITY POINTS                                  │
└─────────────────────────────────────────────────────────────────────────┘

Add New Strategy:
  → Implement LearningStrategy interface
  → Add to Factory strategy map

Add New Question Type:
  → Add to QuestionType enum
  → Update detect_question_type()
  → Map to appropriate strategy

Add New Handler:
  → Extend QuestionHandler
  → Insert into handler chain

Add New Observer:
  → Implement Observer interface
  → Attach to StudentProgressTracker

Modify Configuration:
  → Update .env file or
  → Use config.set() at runtime
```

## Key Benefits of This Architecture

1. **Maintainability**: Each pattern has single responsibility
2. **Extensibility**: Easy to add new strategies, handlers, observers
3. **Testability**: Each component can be tested independently
4. **Flexibility**: Runtime strategy switching, dynamic configuration
5. **Scalability**: Modular design allows feature additions
6. **Readability**: Clear separation of concerns
7. **Reusability**: Patterns can be adapted for other projects

## Component Interactions

- **Singleton** provides config to all components
- **Chain** routes questions to appropriate handlers
- **Factory** detects types and creates strategies
- **Strategy** generates learning-focused prompts
- **Observer** tracks all learning activities
- **OLLAMA** generates AI responses

All coordinated by **StudyAssistant** core service.
