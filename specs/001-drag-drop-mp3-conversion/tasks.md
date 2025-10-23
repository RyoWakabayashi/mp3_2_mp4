# Tasks: Drag & Drop MP3 to MP4 Conversion

**Input**: Design documents from `/specs/001-drag-drop-mp3-conversion/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included for comprehensive validation of the desktop application

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Desktop application with GUI and core conversion logic

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan with src/, tests/, assets/, docs/ directories
- [x] T002 Initialize Python project with requirements.txt and mise configuration in .mise.toml
- [x] T003 [P] Configure development dependencies in requirements-dev.txt (pytest, pytest-qt, black, flake8, mypy)
- [x] T004 [P] Setup sample MP3 files for testing in assets/samples/
- [x] T005 [P] Create application icons in assets/icons/ for Windows and macOS
- [x] T006 [P] Configure GitHub Actions CI pipeline in .github/workflows/ci.yml
- [x] T007 Create main.py entry point in src/main.py with basic argument parsing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Create base data models in src/models/__init__.py and src/models/audio_file.py
- [x] T009 Create ConversionJob model in src/models/conversion_job.py with status enumeration
- [x] T010 Create VideoFile model in src/models/video_file.py with output specifications
- [x] T011 Create ApplicationState model in src/models/application_state.py for global state management
- [x] T012 Setup FFmpeg integration service in src/services/ffmpeg_service.py with validation and conversion methods
- [x] T013 Create file validation utilities in src/utils/file_validator.py for MP3 format checking
- [x] T014 [P] Setup error handling framework in src/utils/error_handler.py with user-friendly messages
- [x] T015 [P] Create logging configuration in src/utils/logger.py with debug and production modes
- [x] T016 Create base GUI application window in src/gui/main_window.py using tkinter + customtkinter

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Single File Conversion (Priority: P1) 🎯 MVP

**Goal**: Enable drag-and-drop of single MP3 file with progress indicator and MP4 output

**Independent Test**: Drag one MP3 file onto application window, verify MP4 created with identical audio and black video

### Tests for User Story 1

- [x] T017 [P] [US1] Unit test for single file validation in tests/unit/test_file_validator.py
- [x] T018 [P] [US1] Unit test for FFmpeg conversion in tests/unit/test_ffmpeg_service.py
- [x] T019 [P] [US1] Integration test for end-to-end single file conversion in tests/integration/test_single_conversion.py
- [x] T020 [P] [US1] GUI automation test for drag-drop interface in tests/gui/test_drag_drop.py

### Implementation for User Story 1

- [x] T021 [P] [US1] Implement drag-and-drop handler in src/gui/drag_drop_handler.py (DropArea widget)
- [x] T022 [P] [US1] Create progress indicator widget in src/gui/progress_widget.py (ProgressDisplay)
- [x] T023 [US1] Implement single file conversion service in src/services/conversion_service.py (via ConversionController)
- [x] T024 [US1] Add file validation before conversion in src/services/validation_service.py (FileValidator + FileValidationController)
- [x] T025 [US1] Integrate progress callbacks with GUI in src/gui/main_window.py
- [x] T026 [US1] Add error display dialogs in src/gui/error_dialog.py (via ErrorHandler)
- [x] T027 [US1] Implement output filename generation in src/utils/filename_utils.py (SettingsService.generate_output_path)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently ✅

---

## Phase 4: User Story 2 - Multiple File Batch Conversion (Priority: P2)

**Goal**: Enable drag-and-drop of multiple MP3 files with individual progress tracking

**Independent Test**: Drag 3-5 MP3 files simultaneously, verify all are converted with individual progress indicators

### Tests for User Story 2

- [x] T028 [P] [US2] Unit test for batch job queue management in tests/unit/test_job_queue.py
- [x] T029 [P] [US2] Integration test for multiple file conversion in tests/integration/test_batch_conversion.py
- [x] T030 [P] [US2] GUI test for multiple file progress display in tests/gui/test_batch_progress.py

### Implementation for User Story 2

- [x] T031 [P] [US2] Create job queue manager in src/services/job_queue_service.py (ConversionController handles queue)
- [x] T032 [P] [US2] Extend progress widget for multiple files in src/gui/batch_progress_widget.py (ProgressDisplay supports multiple)
- [x] T033 [US2] Implement sequential processing logic in src/services/batch_processor.py (ConversionController)
- [x] T034 [US2] Add batch conversion controls (pause/resume/cancel) in src/gui/batch_controls.py (action buttons in MainWindow)
- [x] T035 [US2] Extend drag-drop handler for multiple files in src/gui/drag_drop_handler.py (DropArea + FileListWidget)
- [x] T036 [US2] Add batch completion notifications in src/gui/notification_service.py (MessageBox notifications)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently ✅

---

## Phase 5: User Story 3 - Error Recovery and File Validation (Priority: P3)

**Goal**: Graceful handling of invalid files with clear error messages and recovery options

**Independent Test**: Drag corrupted/invalid files, verify appropriate error messages without application crash

### Tests for User Story 3

- [ ] T037 [P] [US3] Unit test for file corruption detection in tests/unit/test_corruption_detection.py
- [ ] T038 [P] [US3] Unit test for error message generation in tests/unit/test_error_messages.py
- [ ] T039 [P] [US3] Integration test for error recovery scenarios in tests/integration/test_error_recovery.py
- [ ] T040 [P] [US3] GUI test for error dialog interactions in tests/gui/test_error_dialogs.py

### Implementation for User Story 3

- [ ] T041 [P] [US3] Implement advanced file validation in src/services/advanced_validator.py
- [ ] T042 [P] [US3] Create detailed error classification in src/utils/error_classifier.py
- [ ] T043 [P] [US3] Design user-friendly error dialogs in src/gui/advanced_error_dialog.py
- [ ] T044 [US3] Add file size and format warnings in src/services/validation_service.py
- [ ] T045 [US3] Implement retry mechanisms for recoverable errors in src/services/retry_service.py
- [ ] T046 [US3] Add system resource monitoring in src/utils/system_monitor.py
- [ ] T047 [US3] Create error reporting and logging in src/services/error_reporter.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T048 [P] Create Japanese user manual in docs/manual_jp.md with screenshots and step-by-step instructions
- [x] T049 [P] Create build and deployment guide in docs/build.md for PyInstaller packaging
- [x] T050 [P] Implement application settings persistence in src/services/settings_service.py
- [ ] T051 [P] Add keyboard shortcuts and accessibility features in src/gui/accessibility.py
- [x] T052 [P] Create PyInstaller build script in build.py for cross-platform distribution
- [ ] T053 Code cleanup and refactoring for production readiness
- [ ] T054 Performance optimization for large file handling and memory usage
- [ ] T055 [P] Add comprehensive unit tests for edge cases in tests/unit/test_edge_cases.py
- [ ] T056 Security review and input sanitization across all components
- [ ] T057 [P] Create Windows executable packaging with bundled FFmpeg in dist/
- [x] T058 [P] Create macOS application bundle for development testing
- [ ] T059 Final integration testing on clean Windows and macOS systems
- [ ] T060 Run quickstart.md validation and update documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 drag-drop handler but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances validation from US1 but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services (Phase 2 provides base models)
- Services before GUI components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- GUI components within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for single file validation in tests/unit/test_file_validator.py"
Task: "Unit test for FFmpeg conversion in tests/unit/test_ffmpeg_service.py"
Task: "Integration test for end-to-end single file conversion in tests/integration/test_single_conversion.py"
Task: "GUI automation test for drag-drop interface in tests/gui/test_drag_drop.py"

# Launch parallel GUI components for User Story 1:
Task: "Implement drag-and-drop handler in src/gui/drag_drop_handler.py"
Task: "Create progress indicator widget in src/gui/progress_widget.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Create basic Windows executable for user testing

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Create MVP build (basic single file conversion)
3. Add User Story 2 → Test independently → Create enhanced build (batch processing)
4. Add User Story 3 → Test independently → Create robust build (error handling)
5. Polish phase → Production-ready distribution packages

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (core conversion)
   - Developer B: User Story 2 (batch processing)
   - Developer C: User Story 3 (error handling)
3. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 60
- **Setup Phase**: 7 tasks
- **Foundational Phase**: 9 tasks
- **User Story 1**: 11 tasks (4 tests + 7 implementation)
- **User Story 2**: 9 tasks (3 tests + 6 implementation)  
- **User Story 3**: 11 tasks (4 tests + 7 implementation)
- **Polish Phase**: 13 tasks

**Parallel Opportunities**: 32 tasks marked [P] can run in parallel within their phases

**Independent Test Criteria**:
- **US1**: Single MP3 drag-drop → MP4 output with progress indicator
- **US2**: Multiple MP3 drag-drop → All files converted with individual progress
- **US3**: Invalid file drag-drop → Clear error messages without crash

**Suggested MVP Scope**: User Story 1 only (single file conversion with basic drag-drop interface)

**Format Validation**: ✅ All tasks follow required checklist format with Task ID, optional [P] and [Story] labels, and specific file paths