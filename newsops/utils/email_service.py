import smtplib
from email.message import EmailMessage
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

def send_mock_fallback_alert(domain: str, error_detail: str):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        return

    try:
        msg = EmailMessage()
        msg.set_content(
            f"The NewsOps system encountered an error connecting to the Gemini API.\n\n"
            f"Error details: {error_detail}\n\n"
            f"The system has automatically switched to MOCK DATA mode for the domain: {domain}.\n"
            f"Please update the GEMINI_API_KEY in the .env file to restore live API connectivity."
        )
        msg['Subject'] = f"[NewsOps Alert] System Switched to Mock Data Mode ({domain})"
        msg['From'] = SMTP_USER
        msg['To'] = SMTP_USER

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        import logging
        logging.error(f"Failed to send mock fallback email alert: {e}")


def send_html_report_email(session_id: str, session: dict, artifacts: list, recipient_email: str = None):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        raise ValueError("SMTP credentials are not configured in the .env file.")

    # Find master brief
    mb = {}
    for a in artifacts:
        # Check if it has a content dictionary and is master_brief
        if getattr(a, 'artifact_type', '') == 'master_brief':
            mb = getattr(a, 'content', {}) or {}
            break
        elif isinstance(a, dict) and a.get('artifact_type') == 'master_brief':
            mb = a.get('content', {}) or {}
            break

    if not mb:
        # Fallback using whatever keys are in the session dict
        mb = {
            "insight": session.get("insight") or session.get("input_preview") or "",
            "severity_label": session.get("severity_label") or session.get("severityLabel") or "Medium",
            "kpis_affected": session.get("kpis_affected") or [],
            "top_action": session.get("top_action") or {},
            "alternative_actions": session.get("alternative_actions") or []
        }

    # Generate HTML content
    kpis_html = ""
    for kpi in mb.get("kpis_affected", []):
        direction_color = "#10b981" if kpi.get("direction") == "increase" else ("#ef4444" if kpi.get("direction") == "decrease" else "#f59e0b")
        kpis_html += f"""
        <tr style="border-bottom: 1px solid #475569;">
            <td style="padding: 10px; color: #e2e8f0;">{kpi.get('kpi', 'N/A')}</td>
            <td style="padding: 10px; color: #e2e8f0;">{kpi.get('current_value', 'N/A')} {kpi.get('current_unit', '') or kpi.get('unit', '')}</td>
            <td style="padding: 10px; color: {direction_color}; font-weight: bold;">{kpi.get('projected_value', 'N/A')} {kpi.get('current_unit', '') or kpi.get('unit', '')} ({kpi.get('direction', '')})</td>
        </tr>
        """
    if not kpis_html:
        kpis_html = "<tr><td colspan='3' style='padding: 10px; text-align: center; color: #94a3b8;'>No key performance indicators affected.</td></tr>"

    alt_actions_html = ""
    for act in mb.get("alternative_actions", []):
        alt_actions_html += f"""
        <li style="margin-bottom: 8px; color: #cbd5e1;">
            <strong>{act.get('action_type', 'Action')}:</strong> {act.get('description', '')}
        </li>
        """
    if not alt_actions_html:
        alt_actions_html = "<li style='color: #94a3b8;'>No alternative actions proposed.</li>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Nexus AI Intelligence Brief</title>
    </head>
    <body style="font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; border: 1px solid #334155; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #3b82f6, #8b5cf6); padding: 24px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px;">NEXUS AI REPORT</h1>
                <p style="margin: 4px 0 0 0; color: #e2e8f0; font-size: 14px;">Executive Intelligence Brief</p>
            </div>
            
            <!-- Metadata Body -->
            <div style="padding: 24px;">
                <div style="display: block; margin-bottom: 20px; font-size: 13px; color: #94a3b8; border-bottom: 1px solid #334155; padding-bottom: 12px;">
                    <div style="margin-bottom: 4px;"><strong>Session ID:</strong> #{session_id}</div>
                    <div style="margin-bottom: 4px;"><strong>Domain:</strong> {session.get('domain', 'general').upper()}</div>
                    <div style="margin-bottom: 4px;"><strong>Severity Level:</strong> <span style="color: #f43f5e; font-weight: bold;">{mb.get('severity_label', 'Medium')}</span></div>
                </div>

                <!-- Insight Section -->
                <div style="background-color: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 24px;">
                    <h3 style="margin-top: 0; color: #3b82f6; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px;">Key Insight</h3>
                    <p style="margin: 0; color: #e2e8f0; font-size: 14px; line-height: 1.6;">{mb.get('insight', '')}</p>
                </div>

                <!-- KPI Table -->
                <h3 style="color: #f8fafc; font-size: 16px; margin-bottom: 12px; border-bottom: 1px solid #334155; padding-bottom: 8px;">Metric Impact Summary</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px; font-size: 14px;">
                    <thead>
                        <tr style="background-color: #334155; text-align: left;">
                            <th style="padding: 8px 10px; color: #94a3b8; font-weight: 600;">Metric / KPI</th>
                            <th style="padding: 8px 10px; color: #94a3b8; font-weight: 600;">Current Value</th>
                            <th style="padding: 8px 10px; color: #94a3b8; font-weight: 600;">Projected Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        {kpis_html}
                    </tbody>
                </table>

                <!-- Top Recommended Action -->
                <h3 style="color: #f8fafc; font-size: 16px; margin-bottom: 12px; border-bottom: 1px solid #334155; padding-bottom: 8px;">Recommended Action Plan</h3>
                <div style="background-color: #1e293b; border: 1px solid #475569; padding: 16px; border-radius: 8px; margin-bottom: 24px;">
                    <div style="display: inline-block; background-color: #10b981; color: #ffffff; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 9999px; text-transform: uppercase; margin-bottom: 8px;">Primary Recommendation</div>
                    <h4 style="margin: 0 0 6px 0; color: #f8fafc; font-size: 15px;">{mb.get('top_action', {}).get('action_type', 'Execute Response Protocol')}</h4>
                    <p style="margin: 0; color: #94a3b8; font-size: 13px; line-height: 1.5;">{mb.get('top_action', {}).get('description', 'No direct description available.')}</p>
                </div>

                <!-- Alternatives -->
                <h3 style="color: #f8fafc; font-size: 15px; margin-bottom: 12px;">Alternative Mitigations Considered</h3>
                <ul style="padding-left: 20px; margin: 0; font-size: 13px; line-height: 1.6;">
                    {alt_actions_html}
                </ul>
            </div>

            <!-- Footer -->
            <div style="background-color: #0f172a; padding: 16px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #1e293b;">
                This executive brief was automatically generated by Nexus AI agentic backend.<br>
                Powered by Google Antigravity • Confirmed Delivery
            </div>
        </div>
    </body>
    </html>
    """

    to_address = recipient_email if recipient_email else SMTP_USER

    msg = EmailMessage()
    msg.set_content("Please enable HTML viewing to see the intelligence report.")
    msg.add_alternative(html_content, subtype='html')
    msg['Subject'] = f"[Nexus AI] Intelligence Dashboard Brief - {session.get('domain', 'general').upper()} (Session #{session_id})"
    msg['From'] = SMTP_USER
    msg['To'] = to_address

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        import logging
        logging.error(f"Failed to send HTML report email: {e}")
        raise ValueError(f"SMTP Error: {e}")
