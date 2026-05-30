import re

file_path = r'd:\AI-SEEKHO-HACKTHON\newsops\routers\session.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports
content = content.replace(
    'from fastapi import APIRouter, HTTPException',
    'from fastapi import APIRouter, HTTPException, Request\nfrom utils.auth_middleware import get_org_from_request'
)

# Add helper
helper = '''
async def _get_org_filter(request: Request):
    org = await get_org_from_request(request)
    if org:
        return AnalysisSession.org_id == org.id
    return None
'''
content = content.replace('router = APIRouter(prefix="/api", tags=["Session"])', 'router = APIRouter(prefix="/api", tags=["Session"])' + '\n' + helper)

# Update get_sessions
content = re.sub(
    r'async def get_sessions\(\):',
    r'async def get_sessions(request: Request):',
    content
)
content = re.sub(
    r'count_result = await db\.execute\(select\(func\.count\(AnalysisSession\.id\)\)\)',
    r'stmt_count = select(func.count(AnalysisSession.id))\n        org_filter = await _get_org_filter(request)\n        if org_filter is not None:\n            stmt_count = stmt_count.where(org_filter)\n        count_result = await db.execute(stmt_count)',
    content
)
content = re.sub(
    r'result = await db\.execute\(\s*select\(AnalysisSession\)\s*\.order_by\(desc\(AnalysisSession\.created_at\)\)\s*\.limit\(20\)\s*\)',
    r'stmt = select(AnalysisSession)\n        org_filter = await _get_org_filter(request)\n        if org_filter is not None:\n            stmt = stmt.where(org_filter)\n        stmt = stmt.order_by(desc(AnalysisSession.created_at)).limit(20)\n        result = await db.execute(stmt)',
    content
)

# Update other endpoints
endpoints = [
    'get_session_trace', 'get_session_status', 'get_session_task_status',
    'export_session_json', 'export_session_csv', 'export_session_pdf_route',
    'stream_session_progress', 'email_session_report'
]

for ep in endpoints:
    if ep == 'email_session_report':
        content = re.sub(
            fr'async def {ep}\(session_id: str, body: EmailReportRequest = EmailReportRequest\(\)\):',
            fr'async def {ep}(session_id: str, request: Request, body: EmailReportRequest = EmailReportRequest()):',
            content
        )
    else:
        content = re.sub(
            fr'async def {ep}\(session_id: str\):',
            fr'async def {ep}(session_id: str, request: Request):',
            content
        )

new_query = '''stmt = select(AnalysisSession).where(AnalysisSession.id == session_id)
        org_filter = await _get_org_filter(request)
        if org_filter is not None:
            stmt = stmt.where(org_filter)
        result = await db.execute(stmt)'''

content = content.replace(
    'result = await db.execute(\n            select(AnalysisSession).where(AnalysisSession.id == session_id)\n        )',
    new_query
)

content = content.replace(
    'check = await db.execute(\n                select(AnalysisSession).where(AnalysisSession.id == session_id)\n            )',
    '''stmt = select(AnalysisSession).where(AnalysisSession.id == session_id)
            org_filter = await _get_org_filter(request)
            if org_filter is not None: stmt = stmt.where(org_filter)
            check = await db.execute(stmt)'''
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
