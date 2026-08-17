"""Plain-text + HTML bodies for transactional email.

Email HTML lives in its own world: no external stylesheets, no flexbox/grid,
every rule inlined on the element (many clients strip <style> blocks), and
layout done with tables so Outlook's Word rendering engine doesn't mangle it.
"""
import html

INK = "#1a1a1a"
MUTED = "#6a6a6a"
FAINT = "#9a9a9a"
PAGE_BG = "#f6f5f1"
CARD_BG = "#ffffff"
BORDER = "#ececE6"
FONT_STACK = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def _shell(
    *,
    title: str,
    preheader: str,
    headline: str,
    intro: str,
    cta_text: str,
    cta_link: str,
    note: str | None,
    footer_note: str,
    footer_tagline: str,
) -> str:
    """Shared card/table shell every transactional email renders through."""
    note_row = (
        f"""
          <tr>
            <td style="padding:24px 40px 0 40px;">
              <p style="margin:0; font-size:13px; line-height:1.6; color:{FAINT};">
                {note}
              </p>
            </td>
          </tr>"""
        if note
        else ""
    )
    return f"""\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="light">
<title>{title}</title>
</head>
<body style="margin:0; padding:0; background-color:{PAGE_BG}; font-family:{FONT_STACK};">
  <!-- preheader, hidden but shows in inbox preview -->
  <div style="display:none; max-height:0; overflow:hidden; opacity:0; mso-hide:all;">
    {preheader}
  </div>
  <div style="display:none; max-height:0; overflow:hidden;">&#8199;&#8199;&#8199;&#8199;&#8199;&#8199;&#8199;&#8199;&#8199;&#8199;&#8199;&#8199;&#8199;&#8199;&#8199;&#8199;</div>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:{PAGE_BG};">
    <tr>
      <td align="center" style="padding:40px 16px;">

        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px; max-width:100%; background-color:{CARD_BG}; border-radius:16px; border:1px solid {BORDER};">

          <!-- brand -->
          <tr>
            <td style="padding:32px 40px 0 40px;">
              <table role="presentation" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="width:32px; height:32px; background-color:{INK}; border-radius:9px; text-align:center; vertical-align:middle;">
                    <span style="font-family:{FONT_STACK}; font-size:15px; font-weight:700; color:#ffffff; line-height:32px;">S</span>
                  </td>
                  <td style="padding-left:10px; font-family:{FONT_STACK}; font-size:16px; font-weight:800; color:{INK}; letter-spacing:-0.02em;">
                    SpeakStudio
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- headline -->
          <tr>
            <td style="padding:32px 40px 0 40px; font-family:{FONT_STACK};">
              <h1 style="margin:0 0 12px 0; font-size:22px; line-height:1.3; font-weight:800; color:{INK}; letter-spacing:-0.01em;">
                {headline}
              </h1>
              <p style="margin:0; font-size:15px; line-height:1.6; color:{MUTED};">
                {intro}
              </p>
            </td>
          </tr>

          <!-- CTA button -->
          <tr>
            <td style="padding:28px 40px 8px 40px;">
              <table role="presentation" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="background-color:{INK}; border-radius:999px;">
                    <a href="{cta_link}" target="_blank"
                       style="display:inline-block; padding:14px 32px; font-family:{FONT_STACK}; font-size:15px; font-weight:600; color:#ffffff; text-decoration:none; border-radius:999px;">
                      {cta_text}
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- fallback link -->
          <tr>
            <td style="padding:16px 40px 0 40px; font-family:{FONT_STACK};">
              <p style="margin:0; font-size:13px; line-height:1.6; color:{FAINT};">
                Or copy and paste this link into your browser:<br>
                <a href="{cta_link}" target="_blank" style="color:{MUTED}; word-break:break-all;">{cta_link}</a>
              </p>
            </td>
          </tr>
{note_row}

          <!-- divider -->
          <tr>
            <td style="padding:28px 40px 0 40px;">
              <div style="border-top:1px solid {BORDER}; line-height:1px; font-size:1px;">&nbsp;</div>
            </td>
          </tr>

          <!-- footer -->
          <tr>
            <td style="padding:20px 40px 32px 40px; font-family:{FONT_STACK};">
              <p style="margin:0; font-size:12px; line-height:1.6; color:{FAINT};">
                {footer_note}
              </p>
            </td>
          </tr>

        </table>

        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px; max-width:100%;">
          <tr>
            <td style="padding:20px 40px; text-align:center; font-family:{FONT_STACK};">
              <p style="margin:0; font-size:12px; color:{FAINT};">
                SpeakStudio &middot; {footer_tagline}
              </p>
            </td>
          </tr>
        </table>

      </td>
    </tr>
  </table>
</body>
</html>
"""


def invite_email_text(username: str, link: str) -> str:
    return (
        f"Hi {username},\n\n"
        "An account has been created for you on SpeakStudio.\n\n"
        f"Set your password to activate it:\n{link}\n\n"
        "This link expires in 48 hours. If you weren't expecting this, you can "
        "safely ignore this email.\n\n"
        "— SpeakStudio"
    )


def invite_email_html(username: str, link: str) -> str:
    u = html.escape(username)
    return _shell(
        title="You're invited to SpeakStudio",
        preheader=f"{u}, set your password to activate your SpeakStudio account.",
        headline="You've been invited to SpeakStudio",
        intro=f"Hi {u}, an account has been created for you. Set a password below to activate it and get started.",
        cta_text="Set your password",
        cta_link=link,
        note=f"This link expires in <strong style=\"color:{MUTED};\">48 hours</strong>.",
        footer_note="If you weren't expecting this invitation, you can safely ignore this email — no account will be activated without setting a password.",
        footer_tagline="sent to confirm an account created on your behalf",
    )


def reset_password_email_text(username: str, link: str) -> str:
    return (
        f"Hi {username},\n\n"
        "We received a request to reset the password for your SpeakStudio account.\n\n"
        f"Reset your password:\n{link}\n\n"
        "This link expires in 1 hour. If you didn't request this, you can safely "
        "ignore this email — your password won't change.\n\n"
        "— SpeakStudio"
    )


def reset_password_email_html(username: str, link: str) -> str:
    u = html.escape(username)
    return _shell(
        title="Reset your SpeakStudio password",
        preheader=f"{u}, reset your SpeakStudio password.",
        headline="Reset your password",
        intro=f"Hi {u}, we received a request to reset the password for your SpeakStudio account.",
        cta_text="Reset password",
        cta_link=link,
        note=f"This link expires in <strong style=\"color:{MUTED};\">1 hour</strong>.",
        footer_note="If you didn't request this, you can safely ignore this email — your password won't change.",
        footer_tagline="sent because a password reset was requested for your account",
    )


def low_credit_email_text(username: str, credits: int, link: str) -> str:
    return (
        f"Hi {username},\n\n"
        f"Your SpeakStudio account has {credits} credits left.\n\n"
        f"Visit your dashboard to keep going:\n{link}\n\n"
        "This is an automatic notice — no action is required unless you'd like to top up.\n\n"
        "— SpeakStudio"
    )


def low_credit_email_html(username: str, credits: int, link: str) -> str:
    u = html.escape(username)
    return _shell(
        title="You're running low on credits",
        preheader=f"{u}, you have {credits} credits left on SpeakStudio.",
        headline="You're running low on credits",
        intro=f"Hi {u}, your SpeakStudio account has <strong style=\"color:{INK};\">{credits} credits</strong> left.",
        cta_text="Go to dashboard",
        cta_link=link,
        note=None,
        footer_note="This is an automatic notice — no action is required unless you'd like to top up.",
        footer_tagline="sent because your account balance is running low",
    )


def expiry_soon_email_text(username: str, expiry_label: str, link: str) -> str:
    return (
        f"Hi {username},\n\n"
        f"Your SpeakStudio account is set to expire on {expiry_label}.\n\n"
        f"Visit your dashboard:\n{link}\n\n"
        "This is an automatic notice — no action is required unless you'd like to renew.\n\n"
        "— SpeakStudio"
    )


def expiry_soon_email_html(username: str, expiry_label: str, link: str) -> str:
    u = html.escape(username)
    return _shell(
        title="Your SpeakStudio account expires soon",
        preheader=f"{u}, your SpeakStudio account expires on {expiry_label}.",
        headline="Your account expires soon",
        intro=f"Hi {u}, your SpeakStudio account is set to expire on <strong style=\"color:{INK};\">{expiry_label}</strong>.",
        cta_text="Go to dashboard",
        cta_link=link,
        note=None,
        footer_note="This is an automatic notice — no action is required unless you'd like to renew.",
        footer_tagline="sent because your account is nearing its expiry date",
    )
