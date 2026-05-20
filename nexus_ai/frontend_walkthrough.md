# Nexus AI Frontend Walkthrough

This document provides a comprehensive walkthrough of the Nexus AI Flutter frontend architecture. It covers the core structure, detailed breakdowns of every screen and widget, service connections, and the full user journey.

---

## 🏗️ 1. Architecture & Core Setup

The application follows a standard Feature-first/Clean Architecture hybrid, separated into `core`, `data`, and `presentation` layers. It uses `Provider` for state management and basic `Navigator.pushNamed` routing.

*   **`main.dart`**: The entry point. Initializes `ChangeNotifierProvider` with `AnalysisProvider` and defines all routes (`/splash`, `/home`, `/analyze`, etc.) in a `MaterialApp` using a dark theme.
*   **`core/constants/`**:
    *   `api_constants.dart`: Handles base URLs. Smartly adapts between `http://10.0.2.2:8000` (Android emulator), `localhost` (iOS emulator), or a custom IP passed via `--dart-define=BACKEND_IP`. Defines endpoint paths like `/api/analyse/text` and `/api/session/{id}/status`.
    *   `app_constants.dart`: Stores branding (Antigravity AI Ops), the 6 supported domains (logistics, business, etc.), domain icons, and agent model mappings (e.g., orchestrator = GPT-4o).
*   **`core/theme/`**: Contains `app_colors.dart`, `app_text_styles.dart`, and `app_theme.dart` which dictate the dark, glassmorphic, premium visual identity (purples, indigos, neon blues).
*   **`core/utils/`**: Utilities like `connectivity_checker.dart` (pings the backend), and `formatters.dart` for formatting dates, percentages, and currencies.

---

## 📡 2. Data & Services Layer

### Models (`data/models/`)
*   **`analysis_request.dart`**: Defines `TextAnalysisRequest` and `UrlAnalysisRequest` DTOs.
*   **`analysis_response.dart`**: The mega-model holding the backend's response. Contains nested models like `KpiAffected`, `TopAction`, `NotificationSent`, and `AllArtifacts`.
*   **`session_trace.dart`**: Holds the list of `AgentArtifactItem` representing individual JSON files/steps produced by the 6 AI agents during the pipeline.
*   **`domain_state.dart`**: Represents the current KPI/state snapshot of a domain.

### Services (`data/services/`)
*   **`api_service.dart`**: A singleton using the `Dio` HTTP client.
    *   Handles all requests to the FastAPI backend: `analyseText`, `analyseUrl`, `analyseFile` (via `FormData`), `getSessionTrace`, `getSessionStatus`, `getDomainState`, and `resetState`.
    *   Has a `_safeCall` wrapper to catch timeouts and connection errors, surfacing them as readable exceptions (e.g., "Cannot reach backend — is Docker running?").

### State Management (`presentation/providers/`)
*   **`AnalysisProvider`**: The central brain of the app.
    *   Holds input state (selected text, URL, file, domain).
    *   Holds the `AnalysisResponse` (`result`) and `currentSessionId`.
    *   Triggers `runAnalysis()` which makes the initial API call and then sets up a timer to **poll** `getSessionStatus()` every 2 seconds.
    *   Updates `agentProgressStep` (1 through 6) and `liveLogs` based on the polling status, notifying listeners to update the UI in real-time.
    *   Saves completed sessions to `SharedPreferences` for the history screen.

---

## 📱 3. Screens Breakdown

### 1. `SplashScreen` (`/splash`)
1. **What the user sees:** A premium radial-glow Antigravity logo, tagline, animated linear progress bar, and a real-time "Backend connected / offline" indicator.
2. **Data read:** None.
3. **API calls:** Pings the backend via `ConnectivityChecker` to see if it's reachable.
4. **Navigation:** User can tap "Get Started" to go to `/onboarding`, or "Sign in" to go to `/login`.
5. **Bugs/Wiring:** The progress bar is a dummy animation (2 seconds) and doesn't actually await initialization before allowing navigation.

### 2. `OnboardingScreen` (`/onboarding`)
1. **What the user sees:** A 3-page swipeable `PageView` explaining features, 6 domains, and the 6 AI Agents.
2. **Data read:** None.
3. **API calls:** None.
4. **Navigation:** Tapping "Next" moves pages. Tapping "Skip" or "Get Started" pushes `/login`.
5. **Bugs/Wiring:** None, purely presentational.

### 3. `LoginScreen` (`/login`)
1. **What the user sees:** Email/password fields, "Sign In" button, Google/Fingerprint mock buttons.
2. **Data read:** None.
3. **API calls:** None.
4. **Navigation:** Tapping "Sign In" simulates a 1-second load, checks if fields aren't empty, and pushes `/home`.
5. **Bugs/Wiring:** Authentication is entirely mocked. No real auth API is called. Forgot Password and Social logins are dead links.

### 4. `HomeScreen` (`/home`)
1. **What the user sees:** Dashboard greeting ("NimZzzz"), overview stats (42 Inputs Processed), a prominent "+ Analyze New Content" button, and mock "Recent Analyses" cards. Has a bottom navigation bar.
2. **Data read:** Reads `AnalysisProvider` to populate the top "Recent Analysis" card if `provider.result != null`.
3. **API calls:** None.
4. **Navigation:** Tapping "+ Analyze" pushes `/analyze`. Bottom Nav taps push `/insight`, `/actions`, `/trace`, `/history`, `/profile`.
5. **Bugs/Wiring:** 
   * **Major Navigation Bug:** The `NexusBottomNav` uses `Navigator.pushNamed()` instead of an `IndexedStack` or `PageView`. Every tab tap pushes a *new* screen onto the navigation stack, which will lead to memory leaks and infinite back-button stacks.
   * Overview stats (42, 15, 9) are hardcoded.

### 5. `AnalyzeScreen` (`/analyze`)
1. **What the user sees:** Grid of input types (PDF, Text, URL, Excel). An animated switcher showing either a text field, URL field, or File picker. "AI Analysis Options" toggles, a Domain Selector, and a "Run AI Analysis" button.
2. **Data read/write:** Reads and writes `selectedInputType`, `selectedDomain`, text/url content, and file bytes to `AnalysisProvider`.
3. **API calls:** Triggers `provider.runAnalysis()` which hits `/api/analyse/{type}`.
4. **Navigation:** On valid input and backend reachability, tapping "Run" pushes `/progress`.
5. **Bugs/Wiring:** AI Analysis Option toggles (Risk Analysis, Policy Analysis, etc.) are UI-only and are not passed to the backend API payload.

### 6. `AgentProgressScreen` (`/progress`)
1. **What the user sees:** A live processing screen showing 5 distinct steps (Parsing, Insights, Impact, Planning, Simulation). Shows a list of "Active Agents", an overall progress bar, and a live trace log box.
2. **Data read:** Watches `agentProgressStep`, `status`, and `liveLogs` from `AnalysisProvider` which update via the 2-second polling loop.
3. **API calls:** None directly (the Provider is polling `/api/session/{id}/status` in the background).
4. **Navigation:** When `provider.status == AnalysisStatus.complete`, a green checkmark overlays the screen, and it automatically `pushReplacementNamed` to `/insight`.
5. **Bugs/Wiring:** PopScope prevents back navigation while loading, which is good, but if the app backgrounds and the timer dies, it might hang.

### 7. `InsightScreen` (`/insight`)
1. **What the user sees:** The core output. Shows a colored Severity Score bar, Key Insight text, a preview of Recommended Actions, Business Impact grid (Cost, Revenue at Risk, KPIs), and a Before/After metric box.
2. **Data read:** Reads the populated `provider.result` (of type `AnalysisResponse`).
3. **API calls:** None.
4. **Navigation:** Buttons to "Simulate Execution" (`/simulate`) or "Full Trace" (`/trace`).
5. **Bugs/Wiring:** Share button copies text to clipboard correctly. UI handles null results gracefully.

### 8. `ActionsScreen` (`/actions`)
1. **What the user sees:** The "Top Recommendation" detailed card with Expected Delta, and a list of "Alternative Actions" below it. Tapping alternatives shows a bottom sheet with feasibility/impact scores.
2. **Data read:** Reads `provider.result.topAction` and `provider.result.alternativeActions`.
3. **API calls:** None.
4. **Navigation:** Tapping "Execute Now" or "Simulate" pushes `/simulate`.
5. **Bugs/Wiring:** None, works as intended based on the data schema.

### 9. `SimulationScreen` (`/simulate`)
1. **What the user sees:** A visual simulation of the chosen action being executed. Shows the action details, an animated execution log appearing line-by-line, a Before/After State Change block, and a simulated API Payload code block.
2. **Data read:** Reads `provider.result`. Looks for `execLog` in artifacts, otherwise falls back to a hardcoded `_defaultEntries` list.
3. **API calls:** None. The execution is simulated on the frontend using a `Timer` to reveal logs.
4. **Navigation:** After logs finish animating (about 5-6 seconds), a shimmering "View Results" button appears, which pushes to `/results`.
5. **Bugs/Wiring:** The API call preview text block is UI-only; it does not actually execute a secondary POST request to the backend.

### 10. `ResultsScreen` (`/results`)
1. **What the user sees:** A massive bouncing green checkmark, Execution Results (Campaign Created, Notifications Sent), Projected Outcomes, and a vertical "Execution Timeline" tracking the 4 main stages with timestamps.
2. **Data read:** Reads `provider.result` and its nested `artifacts` to pull actual timestamps (`t1`, `t2`, etc.).
3. **API calls:** None.
4. **Navigation:** "New Analysis" clears the provider and pops back to `/home`. "Export PDF" opens a URL in the external browser.
5. **Bugs/Wiring:** "Export PDF" actually just launches the backend JSON trace URL in the browser, not a generated PDF.

### 11. `TraceScreen` (`/trace`)
1. **What the user sees:** A developer/audit view showing the exact JSON outputs of every agent in the multi-agent pipeline (Task Plan, Signals, Impact, Actions, Context, Master Brief).
2. **Data read:** Gets `sessionId` from `provider.currentSessionId` or route arguments.
3. **API calls:** Makes a direct GET call to `/api/session/{id}/trace` via `ApiService`.
4. **Navigation:** "Export" opens the JSON endpoint in browser.
5. **Bugs/Wiring:** Shows a shimmer loader perfectly, handles network failures with a "Retry" button.

### 12. `WorkflowScreen` (`/workflow`)
1. **What the user sees:** A static UI showing "Decision Flow" (Insight -> Impact -> Action -> Execution) and an Agent Timeline.
2. **Data read:** Reads `result?.topAction.justification` from Provider for the reasoning text.
3. **API calls:** None.
4. **Navigation:** None.
5. **Bugs/Wiring:** The timeline tab is completely hardcoded (`_timelineEntries`) rather than using real data, unlike `ResultsScreen` or `TraceScreen`.

### 13. `ProfileScreen` (`/profile`)
1. **What the user sees:** User profile details, general settings list, and a prominent "Reset Domain State" button.
2. **Data read:** None.
3. **API calls:** Tapping "Reset Domain State" triggers `ApiService().resetState()` which drops backend mock DB tables.
4. **Navigation:** Log Out clears stack and pushes `/login`.
5. **Bugs/Wiring:** All settings items (Edit Profile, Language, Theme) are dummy UI rows with no tap handlers.

---

## 🧩 4. Key Widgets

*   **`NexusBottomNav`**: Custom blur/glassmorphic bottom navigation. *Bug noted above regarding navigation stack accumulation.*
*   **`NexusButton`**: The standard CTA. Supports primary and outline variants, and has a built-in `isLoading` state (shows CircularProgressIndicator).
*   **`NexusCard`**: Standard container with borders, padding, and subtle background colors.
*   **`LiveLogView`**: Auto-scrolling ListView inside `AgentProgressScreen` that listens to strings appended to `provider.liveLogs` and displays them with a monospace font.
*   **`DomainSelector`**: Horizontal scrolling list of domains (Logistics, Finance, etc.) using `AppConstants.domains`.
*   **`FileUploadButton`**: Uses the `file_picker` package to grab bytes and filename, passing them to the provider for `multipart/form-data` upload.

---

## 🚀 5. Full User Journey

1. **Launch & Onboarding**: The user launches the app, sees the animated logo, and the app pings the backend to ensure Docker is running. The user skips onboarding and taps through the mock login screen.
2. **Home & Setup**: Arriving at the `HomeScreen`, the user taps "+ Analyze New Content". On the `AnalyzeScreen`, they select a domain (e.g., "Finance"), pick an input type (e.g., "Text"), and tap "Try a sample" to populate the text box with a pre-written Pakistani news snippet.
3. **Processing**: The user taps "Run AI Analysis". The API fires off to FastAPI, and the user is taken to `AgentProgressScreen`. They watch the active agents change and the live trace logs tick by as the frontend polls the backend every 2 seconds.
4. **Insights Review**: Upon completion, the app auto-navigates to `InsightScreen`. The user reviews the High Severity warning, sees the Business Impact (e.g., "PKR 12M at risk"), and views the AI's top autonomous action.
5. **Simulation**: Curious about the action, the user taps "Simulate Execution". On `SimulationScreen`, they watch a simulated terminal log print out API calls and see the "Before" and "After" state change.
6. **Completion**: The simulation finishes, and they proceed to `ResultsScreen`. They see a green checkmark, final projected outcomes, and the complete timeline.
7. **Audit (Optional)**: From the bottom nav, they tap "Logs" (which pushes `TraceScreen`) to audit the raw JSON reasoning of the Orchestrator, Insight, and Action agents.
8. **Reset**: They go to `ProfileScreen` and tap "Reset Domain State" to clear the backend state and do it all again.
