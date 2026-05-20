#!/usr/bin/env bash
# Run the full NewsOps test suite.
# Usage:
#   ./tests/run_tests.sh              # all tests (unit + integration)
#   ./tests/run_tests.sh unit         # unit tests only (no LLM/network calls)
#   ./tests/run_tests.sh integration  # integration tests only
#   ./tests/run_tests.sh imports      # smoke-test: just verify imports
#   ./tests/run_tests.sh coverage     # run all tests + HTML coverage report

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# ── Environment defaults ──────────────────────────────────────────────────────
export GEMINI_API_KEY="${GEMINI_API_KEY:-AIzaSy_mock_gemini_api_key_placeholder}"
export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./test_newsops.db}"
export DEBUG="${DEBUG:-true}"

# ── Generate fixtures if missing ──────────────────────────────────────────────
if [ ! -f "tests/fixtures/sample.pdf" ] || [ ! -f "tests/fixtures/sample.docx" ]; then
    echo "Generating test fixtures..."
    python tests/fixtures/generate_fixtures.py
fi

# ── Run based on argument ─────────────────────────────────────────────────────
MODE="${1:-all}"

case "$MODE" in
    unit)
        echo "Running unit tests..."
        pytest tests/ -m "not integration" -v --tb=short
        ;;
    integration)
        echo "Running integration tests (real OpenAI key required)..."
        if [[ "$GEMINI_API_KEY" == AIzaSy_mock* ]]; then
            echo "WARNING: GEMINI_API_KEY looks like a test key — integration tests will be skipped."
        fi
        pytest tests/ -m integration -v --tb=short
        ;;
    imports)
        echo "Running import smoke tests..."
        pytest tests/test_imports.py -v --tb=short
        ;;
    coverage)
        echo "Running all tests with coverage..."
        pytest tests/ \
            --cov=. \
            --cov-report=html:htmlcov \
            --cov-report=term-missing \
            --cov-omit="tests/*,*/__pycache__/*" \
            -v --tb=short
        echo ""
        echo "Coverage report: htmlcov/index.html"
        ;;
    all|*)
        echo "Running full test suite..."
        pytest tests/ -v --tb=short
        ;;
esac

echo ""
echo "Done."
