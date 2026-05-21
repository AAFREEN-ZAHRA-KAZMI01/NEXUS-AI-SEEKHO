import asyncio, os

os.environ['GEMINI_API_KEY'] = 'AIzaSyDpz93g7D5Yegso3dVorSS3rVBhP_Y8QO4'
os.environ['DATABASE_URL']   = 'sqlite+aiosqlite:///./test_live.db'

import database.models  # register ORM models before create_tables
from database.db import create_tables

TEST_CASES = [
    (
        "logistics",
        "Pakistan State Oil reports fuel prices surged 18% this week. "
        "Lahore-Karachi corridor carriers facing PKR 2.4M extra monthly cost. "
        "OGRA notification effective immediately.",
    ),
    (
        "finance",
        "SBP raises interest rate by 200 basis points. USD/PKR hits 285. "
        "KSE-100 drops 3.2% in single session. Export contracts worth USD 12M at risk.",
    ),
    (
        "healthcare",
        "DRAP issues critical shortage advisory for Insulin. CMH and PIMS report "
        "40% stock depletion. WHO alert issued for Pakistan region. Formulary review required.",
    ),
]

SEP = "=" * 62

async def main():
    await create_tables()
    from pipelines.pipeline import run_pipeline

    for domain, content in TEST_CASES:
        print(f"\n{SEP}")
        print(f"  DOMAIN : {domain.upper()}")
        print(f"  INPUT  : {content[:80]}...")
        print(SEP)
        try:
            result = await run_pipeline(content=content, input_type="text")
            print(f"  detected domain  : {result.get('domain')}")
            print(f"  severity         : {result.get('severity')} ({result.get('severity_label')})")
            print(f"  pipeline status  : {result.get('status')}")
            print(f"  execution status : {result.get('execution_status')}")
            print(f"  mock_mode        : {result.get('mock_mode', False)}")
            print(f"  insight          : {str(result.get('insight', ''))[:130]}")
            top = result.get("top_action") or {}
            print(f"  top_action       : {top.get('action_type', 'N/A')}  -->  {top.get('api_endpoint', 'N/A')}")
            delta = result.get("delta", {})
            print(f"  state delta      : {dict(list(delta.items())[:3])}")
            notifs = result.get("notifications_sent", [])
            print(f"  notifications    : {len(notifs)} sent")
            print(f"  duration         : {result.get('duration_seconds')}s")
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{SEP}")
    print("  ALL TESTS COMPLETE")
    print(SEP)

asyncio.run(main())
