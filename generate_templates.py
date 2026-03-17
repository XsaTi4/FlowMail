import json
import os
from textwrap import dedent


TEMPLATES_DIR = 'data/templates'
os.makedirs(TEMPLATES_DIR, exist_ok=True)

FONT_STACK = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


def tmpl(name, html):
    return {
        "name": name,
        "html": dedent(html).strip().replace("__FONT__", FONT_STACK),
    }


# Premium base templates.
templates = [
    tmpl(
        "Luxe: Welcome",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 24px; overflow: hidden; box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);">
            <div style="padding: 30px 32px; background: linear-gradient(135deg, #0f172a 0%, #334155 100%);">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.18em; color: #94a3b8;">New account</div>
                <h1 style="margin: 12px 0 0 0; color: #ffffff; font-size: 32px; line-height: 1.1; font-weight: 800;">Welcome to the inner circle</h1>
                <p style="margin: 12px 0 0 0; color: #cbd5e1; font-size: 16px; line-height: 1.7;">Hi {{first_name}}, thanks for joining FlowMail. Your workspace is now ready for polished campaigns, better pacing, and cleaner delivery.</p>
            </div>
            <div style="padding: 32px; color: #334155; line-height: 1.7;">
                <div style="display: grid; gap: 12px; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-bottom: 28px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px;">
                        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">Fast setup</div>
                        <div style="margin-top: 8px; font-size: 15px; color: #0f172a; font-weight: 700;">Templates, queue, and send controls in one place.</div>
                    </div>
                    <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 14px; padding: 16px;">
                        <div style="font-size: 12px; color: #2563eb; text-transform: uppercase; letter-spacing: 0.08em;">Safer pacing</div>
                        <div style="margin-top: 8px; font-size: 15px; color: #0f172a; font-weight: 700;">Delay, jitter, and pause controls stay easy to reach.</div>
                    </div>
                    <div style="background: #fef3c7; border: 1px solid #fde68a; border-radius: 14px; padding: 16px;">
                        <div style="font-size: 12px; color: #b45309; text-transform: uppercase; letter-spacing: 0.08em;">Live tracking</div>
                        <div style="margin-top: 8px; font-size: 15px; color: #0f172a; font-weight: 700;">See sent, failed, and pending recipients at a glance.</div>
                    </div>
                </div>
                <p style="margin: 0 0 24px 0; font-size: 16px;">The goal is simple: keep your campaigns premium, deliberate, and easy to recover if a session is interrupted.</p>
                <div style="text-align: center; margin: 28px 0 8px 0;">
                    <a href="#" style="background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #ffffff; padding: 14px 30px; text-decoration: none; border-radius: 999px; font-weight: 700; font-size: 15px; display: inline-block;">Explore your dashboard</a>
                </div>
                <p style="font-size: 13px; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 20px; margin-top: 28px;">Need help getting started? Our support team is ready whenever you are.</p>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Insight: Weekly Digest",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%); padding: 20px;">
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);">
                <div style="padding: 22px 28px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; gap: 16px;">
                    <div>
                        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.12em;">Weekly digest</div>
                        <h2 style="margin: 8px 0 0 0; font-size: 24px; color: #0f172a;">What moved the numbers this week</h2>
                    </div>
                    <div style="background: #eff6ff; border: 1px solid #dbeafe; color: #2563eb; border-radius: 999px; padding: 8px 14px; font-size: 13px; font-weight: 700; white-space: nowrap;">{{date}}</div>
                </div>
                <div style="padding: 28px; color: #334155; line-height: 1.7;">
                    <p style="margin: 0 0 20px 0; font-size: 16px;">This edition highlights the clearest patterns from the past seven days, the experiments worth repeating, and the delivery changes that made the biggest difference.</p>
                    <div style="display: grid; gap: 14px; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-bottom: 22px;">
                        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px;">
                            <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b;">Open rate</div>
                            <div style="margin-top: 8px; font-size: 28px; font-weight: 800; color: #0f172a;">42%</div>
                            <div style="margin-top: 6px; color: #64748b; font-size: 14px;">Up 8 points over the previous issue.</div>
                        </div>
                        <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 16px; padding: 18px;">
                            <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #2563eb;">Click-through</div>
                            <div style="margin-top: 8px; font-size: 28px; font-weight: 800; color: #0f172a;">9.6%</div>
                            <div style="margin-top: 6px; color: #64748b; font-size: 14px;">Best result from the product spotlight block.</div>
                        </div>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #8b5cf6; border-radius: 16px; padding: 20px; margin-bottom: 24px;">
                        <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #8b5cf6;">Featured takeaway</div>
                        <h3 style="margin: 8px 0 0 0; color: #0f172a; font-size: 18px;">Personalization works best when the copy is short, specific, and visually calm.</h3>
                        <p style="margin: 8px 0 0 0; color: #475569; font-size: 14px;">Keep the opening sentence clear, the CTA singular, and the spacing generous enough that each section can breathe.</p>
                    </div>
                    <a href="#" style="color: #2563eb; font-weight: 700; text-decoration: none;">Read the full report -></a>
                </div>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Luxe: Product Reveal",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: #0f172a; border: 1px solid #1e293b; border-radius: 28px; overflow: hidden; box-shadow: 0 24px 60px rgba(15, 23, 42, 0.35);">
            <div style="padding: 42px 34px; background: linear-gradient(135deg, #111827 0%, #1d4ed8 60%, #0f172a 100%);">
                <div style="display: inline-block; padding: 6px 14px; border-radius: 999px; background: rgba(255,255,255,0.12); color: #dbeafe; font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em;">New release</div>
                <h1 style="margin: 18px 0 0 0; color: #ffffff; font-size: 34px; line-height: 1.08; font-weight: 900; letter-spacing: -0.04em;">Designed for teams that care about every send</h1>
                <p style="margin: 14px 0 0 0; color: #cbd5e1; font-size: 17px; line-height: 1.7;">A cleaner sending workflow, sharper template control, and a calmer way to monitor progress from launch to completion.</p>
            </div>
            <div style="padding: 34px; background: #ffffff; color: #334155;">
                <div style="display: grid; gap: 14px; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-bottom: 26px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px; text-align: center;">
                        <div style="font-size: 28px; font-weight: 900; color: #0f172a;">2x</div>
                        <div style="margin-top: 6px; font-size: 13px; color: #64748b;">Faster preparation</div>
                    </div>
                    <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 16px; padding: 18px; text-align: center;">
                        <div style="font-size: 28px; font-weight: 900; color: #1d4ed8;">24/7</div>
                        <div style="margin-top: 6px; font-size: 13px; color: #64748b;">Queue visibility</div>
                    </div>
                    <div style="background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 16px; padding: 18px; text-align: center;">
                        <div style="font-size: 28px; font-weight: 900; color: #7c3aed;">0</div>
                        <div style="margin-top: 6px; font-size: 13px; color: #64748b;">Guesswork in the flow</div>
                    </div>
                </div>
                <p style="margin: 0 0 24px 0; font-size: 16px; line-height: 1.7;">Hi {{first_name}}, the platform update is now live. Everything from import to preview feels tighter, lighter, and easier to control.</p>
                <div style="text-align: center;">
                    <a href="#" style="display: inline-block; background: linear-gradient(135deg, #2563eb, #4f46e5); color: #ffffff; text-decoration: none; padding: 14px 30px; border-radius: 999px; font-weight: 800; font-size: 15px;">Get VIP access</a>
                </div>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Executive: Invitation",
        """
        <div style="font-family: __FONT__; max-width: 560px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; overflow: hidden; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);">
            <div style="padding: 34px 36px; text-align: center; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.2em;">Private invitation</div>
                <h2 style="margin: 14px 0 0 0; font-size: 30px; color: #111827; font-weight: 400; letter-spacing: -0.03em;">Leadership summit 2026</h2>
                <p style="margin: 14px 0 0 0; color: #475569; font-size: 16px; line-height: 1.7;">A focused evening for strategic conversations, product direction, and high-value networking.</p>
            </div>
            <div style="padding: 30px 36px; color: #334155; line-height: 1.7;">
                <div style="display: grid; gap: 12px; grid-template-columns: 1fr 1fr; margin-bottom: 22px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px;">
                        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">Date</div>
                        <div style="margin-top: 6px; font-size: 16px; color: #111827; font-weight: 700;">March 25, 2026</div>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px;">
                        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">Venue</div>
                        <div style="margin-top: 6px; font-size: 16px; color: #111827; font-weight: 700;">Glass House, New York</div>
                    </div>
                </div>
                <p style="margin: 0 0 24px 0;">We would be honored to have you join us for a curated discussion on growth, retention, and the next phase of the roadmap.</p>
                <div style="text-align: center;">
                    <a href="#" style="background: #111827; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 15px; display: inline-block;">Confirm attendance</a>
                </div>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Flash: Limited Offer",
        """
        <div style="font-family: __FONT__; max-width: 620px; margin: 0 auto; background: #fff7ed; border: 1px solid #fdba74; border-radius: 22px; overflow: hidden;">
            <div style="padding: 36px 32px; background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: #ffffff; text-align: center;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.18em; opacity: 0.9;">Limited window</div>
                <h1 style="margin: 12px 0 0 0; font-size: 54px; line-height: 0.95; font-weight: 900; letter-spacing: -0.05em;">40% OFF</h1>
                <p style="margin: 12px 0 0 0; font-size: 18px; line-height: 1.6; opacity: 0.95;">A clean offer block built to convert without feeling noisy.</p>
            </div>
            <div style="padding: 30px 32px; text-align: center; color: #7c2d12;">
                <p style="margin: 0 0 18px 0; font-size: 16px; line-height: 1.7; color: #9a3412;">Use your private code at checkout and keep the rest of the message short, sharp, and confident.</p>
                <div style="display: inline-block; background: #ffffff; border: 2px dashed #fb923c; border-radius: 16px; padding: 18px 26px; margin-bottom: 24px; box-shadow: 0 8px 18px rgba(249, 115, 22, 0.08);">
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; color: #c2410c;">Promo code</div>
                    <div style="margin-top: 8px; font-size: 28px; font-weight: 900; color: #7c2d12; font-family: monospace;">VIP40SALE</div>
                </div>
                <div>
                    <a href="#" style="background: #111827; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 999px; font-weight: 800; display: inline-block;">Shop the offer</a>
                </div>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Confirm: Professional Receipt",
        """
        <div style="font-family: __FONT__; max-width: 620px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; overflow: hidden; box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);">
            <div style="padding: 28px 32px; background: #0f172a; color: #ffffff; display: flex; justify-content: space-between; align-items: center; gap: 16px;">
                <div>
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.14em; color: #94a3b8;">Receipt</div>
                    <h2 style="margin: 8px 0 0 0; font-size: 22px;">Order confirmed</h2>
                </div>
                <div style="font-size: 14px; color: #cbd5e1;">#{{order_id}}</div>
            </div>
            <div style="padding: 32px; color: #334155; line-height: 1.7;">
                <p style="margin: 0 0 18px 0; font-size: 16px;">Hi {{first_name}}, your order is confirmed and the summary below gives you the key details in a calm, readable format.</p>
                <div style="display: grid; gap: 12px; grid-template-columns: 1fr 1fr; margin-bottom: 24px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px;">
                        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">Plan</div>
                        <div style="margin-top: 6px; font-size: 16px; color: #0f172a; font-weight: 700;">Premium subscription</div>
                    </div>
                    <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 14px; padding: 16px;">
                        <div style="font-size: 12px; color: #2563eb; text-transform: uppercase; letter-spacing: 0.08em;">Date</div>
                        <div style="margin-top: 6px; font-size: 16px; color: #0f172a; font-weight: 700;">{{date}}</div>
                    </div>
                </div>
                <table width="100%" style="border-collapse: collapse; margin-bottom: 24px;">
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 14px 0; color: #64748b;">Premium subscription</td>
                        <td style="padding: 14px 0; text-align: right; color: #0f172a; font-weight: 700;">$49.00</td>
                    </tr>
                    <tr>
                        <td style="padding: 14px 0; color: #0f172a; font-weight: 800;">Total</td>
                        <td style="padding: 14px 0; text-align: right; color: #0f172a; font-weight: 800;">$49.00</td>
                    </tr>
                </table>
                <div style="text-align: center;">
                    <a href="#" style="background: #2563eb; color: #ffffff; padding: 13px 28px; text-decoration: none; border-radius: 10px; font-weight: 700; display: inline-block;">View invoice online</a>
                </div>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Security: Alert",
        """
        <div style="font-family: __FONT__; max-width: 560px; margin: 0 auto; background: #ffffff; border: 1px solid #fee2e2; border-radius: 18px; overflow: hidden; box-shadow: 0 12px 30px rgba(127, 29, 29, 0.08);">
            <div style="padding: 24px 30px; background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%); color: #ffffff;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.16em; opacity: 0.9;">Security notice</div>
                <h2 style="margin: 10px 0 0 0; font-size: 24px; line-height: 1.2;">New sign-in detected</h2>
            </div>
            <div style="padding: 30px; color: #334155; line-height: 1.7;">
                <p style="margin: 0 0 18px 0;">We noticed a new login to your account. If this was you, no action is needed. If it was not, review the session details below and secure your account immediately.</p>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px; margin-bottom: 24px;">
                    <p style="margin: 0; color: #475569; font-size: 14px; line-height: 1.8;"><strong style="color: #0f172a;">Location:</strong> {{location}}<br><strong style="color: #0f172a;">Device:</strong> {{device}}<br><strong style="color: #0f172a;">Time:</strong> {{date}}</p>
                </div>
                <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
                    <a href="#" style="background: #111827; color: #ffffff; padding: 12px 22px; text-decoration: none; border-radius: 10px; font-weight: 700;">Secure my account</a>
                    <a href="#" style="background: #ffffff; color: #b91c1c; padding: 12px 22px; text-decoration: none; border-radius: 10px; font-weight: 700; border: 1px solid #fecaca;">This was me</a>
                </div>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Connect: Referral",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%); border-radius: 24px; overflow: hidden; color: #ffffff; box-shadow: 0 20px 50px rgba(79, 70, 229, 0.24);">
            <div style="display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 0;">
                <div style="padding: 40px 36px;">
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.18em; color: #c7d2fe;">Referral program</div>
                    <h2 style="margin: 14px 0 0 0; font-size: 32px; line-height: 1.1; font-weight: 900; letter-spacing: -0.04em;">Give $20, get $20</h2>
                    <p style="margin: 16px 0 0 0; font-size: 16px; line-height: 1.7; color: #e0e7ff;">A simple referral message with a polished reward block and a clean CTA that keeps the attention on the offer.</p>
                    <div style="margin-top: 28px; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.16); border-radius: 16px; padding: 18px;">
                        <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; color: #c7d2fe;">Your link</div>
                        <div style="margin-top: 8px; font-size: 20px; font-weight: 800; font-family: monospace;">flowmail.io/r/{{referral_code}}</div>
                    </div>
                </div>
                <div style="padding: 40px 28px; background: rgba(15, 23, 42, 0.18); display: flex; flex-direction: column; justify-content: center; gap: 14px;">
                    <div style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.16); border-radius: 16px; padding: 18px;">
                        <div style="font-size: 12px; color: #c7d2fe; text-transform: uppercase; letter-spacing: 0.1em;">Reward</div>
                        <div style="margin-top: 8px; font-size: 18px; font-weight: 800;">Two-way credit</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.16); border-radius: 16px; padding: 18px;">
                        <div style="font-size: 12px; color: #c7d2fe; text-transform: uppercase; letter-spacing: 0.1em;">Audience</div>
                        <div style="margin-top: 8px; font-size: 18px; font-weight: 800;">Friends who value clean tools</div>
                    </div>
                    <a href="#" style="margin-top: 4px; background: #ffffff; color: #4f46e5; text-decoration: none; padding: 13px 22px; border-radius: 10px; font-weight: 800; text-align: center;">Share your link</a>
                </div>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Bento: Product Update",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 24px; padding: 26px;">
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; padding: 24px; margin-bottom: 18px;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.16em; color: #64748b;">Product update</div>
                <h2 style="margin: 10px 0 0 0; color: #0f172a; font-size: 28px; line-height: 1.15;">A calmer way to run campaigns</h2>
                <p style="margin: 12px 0 0 0; color: #475569; font-size: 16px; line-height: 1.7;">This update focuses on the details that make everyday sending feel deliberate instead of noisy.</p>
            </div>
            <div style="display: grid; gap: 14px; grid-template-columns: repeat(3, minmax(0, 1fr));">
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px;">
                    <div style="font-size: 12px; color: #2563eb; text-transform: uppercase; letter-spacing: 0.08em;">Queue</div>
                    <div style="margin-top: 8px; font-size: 16px; color: #0f172a; font-weight: 800;">Cleaner recovery flow</div>
                </div>
                <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 16px; padding: 18px;">
                    <div style="font-size: 12px; color: #2563eb; text-transform: uppercase; letter-spacing: 0.08em;">Builder</div>
                    <div style="margin-top: 8px; font-size: 16px; color: #0f172a; font-weight: 800;">Sharper template previews</div>
                </div>
                <div style="background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 16px; padding: 18px;">
                    <div style="font-size: 12px; color: #7c3aed; text-transform: uppercase; letter-spacing: 0.08em;">Settings</div>
                    <div style="margin-top: 8px; font-size: 16px; color: #0f172a; font-weight: 800;">Safer pacing controls</div>
                </div>
            </div>
            <div style="margin-top: 18px; background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%); color: #ffffff; border-radius: 18px; padding: 22px; display: flex; justify-content: space-between; align-items: center; gap: 16px;">
                <div>
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; color: #bfdbfe;">Ready when you are</div>
                    <div style="margin-top: 8px; font-size: 18px; font-weight: 800;">Launch the updated flow in one click.</div>
                </div>
                <a href="#" style="background: #ffffff; color: #1d4ed8; padding: 12px 18px; text-decoration: none; border-radius: 999px; font-weight: 800; white-space: nowrap;">See whats new</a>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Elegant: Feedback",
        """
        <div style="font-family: __FONT__; max-width: 560px; margin: 0 auto; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 24px; padding: 40px 32px; text-align: center; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);">
            <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.16em; color: #64748b;">Feedback</div>
            <h2 style="margin: 12px 0 0 0; color: #111827; font-size: 28px; line-height: 1.2;">How are we doing?</h2>
            <p style="margin: 14px 0 0 0; color: #6b7280; font-size: 16px; line-height: 1.7;">Your opinion helps us refine the product without adding noise to the experience.</p>
            <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; margin: 28px 0;">
                <a href="#" style="background: #f8fafc; border: 1px solid #e2e8f0; color: #0f172a; text-decoration: none; padding: 12px 18px; border-radius: 999px; font-weight: 700;">Poor</a>
                <a href="#" style="background: #f8fafc; border: 1px solid #e2e8f0; color: #0f172a; text-decoration: none; padding: 12px 18px; border-radius: 999px; font-weight: 700;">Average</a>
                <a href="#" style="background: #2563eb; border: 1px solid #2563eb; color: #ffffff; text-decoration: none; padding: 12px 18px; border-radius: 999px; font-weight: 700;">Excellent</a>
            </div>
            <p style="margin: 0; font-size: 13px; color: #9ca3af;">Takes less than 30 seconds.</p>
        </div>
        """,
    ),
    tmpl(
        "SaaS: Feature Adoption",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; overflow: hidden;">
            <div style="padding: 28px 32px; background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%); border-bottom: 1px solid #e2e8f0;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.16em; color: #64748b;">Feature adoption</div>
                <h2 style="margin: 12px 0 0 0; color: #111827; font-size: 26px; line-height: 1.2;">Three small changes that make sending easier</h2>
            </div>
            <div style="padding: 30px 32px; display: grid; gap: 14px; grid-template-columns: 1fr;">
                <div style="display: grid; grid-template-columns: 64px 1fr; gap: 14px; align-items: start; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 16px;">
                    <div style="background: #eff6ff; color: #2563eb; border-radius: 14px; height: 48px; display: flex; align-items: center; justify-content: center; font-weight: 900;">01</div>
                    <div><div style="font-weight: 800; color: #0f172a;">Enable smart queuing</div><div style="margin-top: 6px; color: #64748b; font-size: 14px; line-height: 1.7;">Keep the queue visible while you edit recipients, templates, and pacing rules.</div></div>
                </div>
                <div style="display: grid; grid-template-columns: 64px 1fr; gap: 14px; align-items: start; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 16px;">
                    <div style="background: #ecfeff; color: #0891b2; border-radius: 14px; height: 48px; display: flex; align-items: center; justify-content: center; font-weight: 900;">02</div>
                    <div><div style="font-weight: 800; color: #0f172a;">Use jitter for natural spacing</div><div style="margin-top: 6px; color: #64748b; font-size: 14px; line-height: 1.7;">Randomized delay keeps timing from feeling mechanical while preserving control.</div></div>
                </div>
                <div style="display: grid; grid-template-columns: 64px 1fr; gap: 14px; align-items: start; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 16px;">
                    <div style="background: #fef3c7; color: #b45309; border-radius: 14px; height: 48px; display: flex; align-items: center; justify-content: center; font-weight: 900;">03</div>
                    <div><div style="font-weight: 800; color: #0f172a;">Recover sessions quickly</div><div style="margin-top: 6px; color: #64748b; font-size: 14px; line-height: 1.7;">Resume from the exact point a send stopped without rebuilding the campaign.</div></div>
                </div>
            </div>
            <div style="padding: 0 32px 32px 32px; text-align: center;">
                <a href="#" style="background: #111827; color: #ffffff; text-decoration: none; padding: 13px 24px; border-radius: 10px; font-weight: 800; display: inline-block;">Try the new flow</a>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Noir: Event RSVP",
        """
        <div style="font-family: __FONT__; max-width: 620px; margin: 0 auto; background: #0f172a; color: #ffffff; border-radius: 26px; overflow: hidden; box-shadow: 0 24px 60px rgba(15, 23, 42, 0.35);">
            <div style="padding: 40px 34px; text-align: center; background: linear-gradient(135deg, #111827 0%, #0f172a 100%);">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.2em; color: #94a3b8;">Invitation</div>
                <h1 style="margin: 12px 0 0 0; font-size: 34px; line-height: 1.1; font-weight: 900;">An evening of focused conversation</h1>
                <p style="margin: 14px 0 0 0; color: #cbd5e1; font-size: 16px; line-height: 1.7;">A premium RSVP design for launches, dinners, or private sessions where the message should feel deliberate and exclusive.</p>
            </div>
            <div style="padding: 32px; background: #ffffff; color: #334155;">
                <div style="display: grid; gap: 14px; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-bottom: 24px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px;">
                        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">Date</div>
                        <div style="margin-top: 8px; color: #0f172a; font-size: 16px; font-weight: 800;">{{date}}</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px;">
                        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">Location</div>
                        <div style="margin-top: 8px; color: #0f172a; font-size: 16px; font-weight: 800;">{{location}}</div>
                    </div>
                </div>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; margin-bottom: 24px;">
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; color: #64748b;">Agenda</div>
                    <div style="margin-top: 10px; color: #334155; line-height: 1.8; font-size: 15px;">1. Opening remarks<br>2. Product preview<br>3. Q and A</div>
                </div>
                <div style="text-align: center;">
                    <a href="#" style="background: #ffffff; color: #0f172a; padding: 13px 26px; text-decoration: none; border-radius: 999px; font-weight: 800; border: 1px solid #e2e8f0; display: inline-block;">RSVP now</a>
                </div>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Case Study: Proof",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; overflow: hidden;">
            <div style="padding: 28px 32px; background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%); border-bottom: 1px solid #e2e8f0;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.14em; color: #64748b;">Case study</div>
                <h2 style="margin: 12px 0 0 0; font-size: 28px; color: #0f172a; line-height: 1.15;">How a lean team increased engagement by 45%</h2>
            </div>
            <div style="padding: 32px; color: #334155; line-height: 1.7;">
                <p style="margin: 0 0 22px 0; font-size: 16px;">Hi {{first_name}}, this brief highlights the strategy, copy structure, and delivery changes that created a measurable lift without increasing send volume.</p>
                <div style="display: grid; gap: 14px; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-bottom: 24px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px; text-align: center;"><div style="font-size: 28px; font-weight: 900; color: #0f172a;">45%</div><div style="margin-top: 6px; color: #64748b; font-size: 13px;">Engagement gain</div></div>
                    <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 16px; padding: 18px; text-align: center;"><div style="font-size: 28px; font-weight: 900; color: #1d4ed8;">2.4x</div><div style="margin-top: 6px; color: #64748b; font-size: 13px;">Click lift</div></div>
                    <div style="background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 16px; padding: 18px; text-align: center;"><div style="font-size: 28px; font-weight: 900; color: #7c3aed;">-18%</div><div style="margin-top: 6px; color: #64748b; font-size: 13px;">Fewer complaints</div></div>
                </div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; border-radius: 16px; padding: 18px; margin-bottom: 22px;">
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; color: #2563eb;">What worked</div>
                    <p style="margin: 8px 0 0 0; font-size: 14px; color: #475569;">A shorter lead, one focused CTA, and cleaner segmentation delivered the strongest result.</p>
                </div>
                <a href="#" style="color: #2563eb; font-weight: 800; text-decoration: none;">Download the full case study -></a>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Release Notes: Version 3.0",
        """
        <div style="font-family: __FONT__; max-width: 560px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 22px; padding: 36px; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);">
            <div style="text-align: center; margin-bottom: 26px;">
                <div style="display: inline-block; background: #eff6ff; color: #2563eb; padding: 6px 14px; border-radius: 999px; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.12em;">Version 3.0</div>
                <h1 style="margin: 14px 0 0 0; color: #111827; font-size: 28px; line-height: 1.15;">The desktop upgrade, refined</h1>
                <p style="margin: 10px 0 0 0; color: #6b7280; font-size: 15px; line-height: 1.7;">Sharper previews, better queue handling, and a calmer experience around every send.</p>
            </div>
            <div style="display: grid; gap: 14px;">
                <div style="padding: 18px; border: 1px solid #e2e8f0; border-radius: 16px; background: #f8fafc;"><div style="color: #0f172a; font-weight: 800;">Native performance</div><div style="margin-top: 6px; color: #64748b; font-size: 14px; line-height: 1.7;">The flow feels lighter across settings, builder, and the dashboard.</div></div>
                <div style="padding: 18px; border: 1px solid #e2e8f0; border-radius: 16px; background: #ffffff;"><div style="color: #0f172a; font-weight: 800;">Better recovery</div><div style="margin-top: 6px; color: #64748b; font-size: 14px; line-height: 1.7;">Resume sessions with clearer progress and less guesswork.</div></div>
                <div style="padding: 18px; border: 1px solid #e2e8f0; border-radius: 16px; background: #f8fafc;"><div style="color: #0f172a; font-weight: 800;">Cleaner templates</div><div style="margin-top: 6px; color: #64748b; font-size: 14px; line-height: 1.7;">A more premium look for every system template in the gallery.</div></div>
            </div>
            <div style="margin-top: 24px; text-align: center;">
                <a href="#" style="display: inline-block; background: #111827; color: #ffffff; padding: 13px 24px; text-decoration: none; border-radius: 10px; font-weight: 800;">View changelog</a>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Invoice: Standard",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; overflow: hidden;">
            <div style="padding: 28px 32px; background: #111827; color: #ffffff; display: flex; justify-content: space-between; align-items: center; gap: 16px;">
                <div>
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.14em; color: #9ca3af;">Invoice</div>
                    <h2 style="margin: 8px 0 0 0; font-size: 22px;">Premium subscription</h2>
                </div>
                <div style="font-size: 14px; color: #cbd5e1;">#INV-2026-001</div>
            </div>
            <div style="padding: 32px; color: #334155; line-height: 1.7;">
                <div style="display: grid; gap: 12px; grid-template-columns: 1fr 1fr; margin-bottom: 24px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px;"><div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">Bill to</div><div style="margin-top: 6px; color: #0f172a; font-weight: 800;">{{first_name}} {{last_name}}</div><div style="margin-top: 4px; color: #64748b; font-size: 14px;">{{company}}</div></div>
                    <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 14px; padding: 16px;"><div style="font-size: 12px; color: #2563eb; text-transform: uppercase; letter-spacing: 0.08em;">Issue date</div><div style="margin-top: 6px; color: #0f172a; font-weight: 800;">{{date}}</div></div>
                </div>
                <table width="100%" style="border-collapse: collapse; margin-bottom: 24px;">
                    <tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 14px 0; color: #64748b;">Platform access</td><td style="padding: 14px 0; text-align: right; color: #0f172a; font-weight: 700;">$299.00</td></tr>
                    <tr><td style="padding: 14px 0; color: #0f172a; font-weight: 800;">Total due</td><td style="padding: 14px 0; text-align: right; color: #0f172a; font-weight: 800;">$299.00</td></tr>
                </table>
                <div style="text-align: center;"><a href="#" style="background: #2563eb; color: #ffffff; padding: 13px 26px; text-decoration: none; border-radius: 10px; font-weight: 800; display: inline-block;">Pay now</a></div>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Personal: Simple Note",
        """
        <div style="font-family: __FONT__; max-width: 600px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 36px 34px; color: #334155; line-height: 1.8;">
            <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.14em; color: #64748b;">Personal note</div>
            <h2 style="margin: 12px 0 0 0; color: #111827; font-size: 28px; line-height: 1.2;">A quick thank you</h2>
            <p style="margin: 18px 0 0 0; font-size: 16px;">Hi {{first_name}}, I wanted to send a short note to say thank you for the thoughtful feedback last week. It helped us sharpen the roadmap and simplify the next set of updates.</p>
            <p style="margin: 16px 0 0 0; font-size: 16px;">The next version should feel lighter, clearer, and more intentional.</p>
            <p style="margin: 28px 0 0 0; font-size: 16px;">Best regards,<br><strong>{{sender_name}}</strong></p>
        </div>
        """,
    ),
    tmpl(
        "Verify: Email Confirmation",
        """
        <div style="font-family: __FONT__; max-width: 500px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 22px; padding: 44px 36px; text-align: center; box-shadow: 0 14px 32px rgba(15, 23, 42, 0.06);">
            <div style="width: 66px; height: 66px; border-radius: 20px; margin: 0 auto 18px auto; background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%); display: flex; align-items: center; justify-content: center; font-size: 30px;">@</div>
            <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.16em; color: #64748b;">Verification</div>
            <h2 style="margin: 12px 0 0 0; color: #111827; font-size: 28px; line-height: 1.2;">Confirm your email address</h2>
            <p style="margin: 14px 0 0 0; color: #6b7280; font-size: 16px; line-height: 1.7;">Click the button below to finish setting up your account and unlock the rest of the experience.</p>
            <a href="#" style="display: block; margin-top: 28px; background: #2563eb; color: #ffffff; padding: 14px 16px; text-decoration: none; border-radius: 10px; font-weight: 800;">Verify email</a>
            <p style="margin: 20px 0 0 0; color: #9ca3af; font-size: 13px; line-height: 1.6;">If you did not request this, you can safely ignore it.</p>
        </div>
        """,
    ),
]


additional_templates = [
    tmpl(
        "Dark: Cyber Monday",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: #000000; color: #ffffff; border-radius: 26px; overflow: hidden; box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);">
            <div style="padding: 42px 34px; text-align: center; background: radial-gradient(circle at top, #1f2937 0%, #000000 62%);">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.2em; color: #22d3ee;">Limited time event</div>
                <h1 style="margin: 12px 0 0 0; font-size: 60px; line-height: 0.95; font-weight: 900; letter-spacing: -0.06em;">70% OFF</h1>
                <p style="margin: 14px 0 0 0; font-size: 18px; line-height: 1.7; color: #cbd5e1;">A bold, dark theme for a high-contrast offer block that keeps the focus on the discount.</p>
            </div>
            <div style="padding: 30px 34px 40px 34px; background: #0f172a; text-align: center;">
                <div style="display: inline-block; padding: 14px 24px; border: 1px solid #22d3ee; border-radius: 999px; color: #22d3ee; font-size: 15px; font-weight: 800; letter-spacing: 0.08em; margin-bottom: 22px;">NO CODE NEEDED</div>
                <p style="margin: 0 0 24px 0; color: #94a3b8; font-size: 14px; line-height: 1.7;">Discounts are applied automatically at checkout. Keep the copy direct and the CTA unmistakable.</p>
                <a href="#" style="background: linear-gradient(135deg, #22d3ee, #3b82f6); color: #0f172a; text-decoration: none; padding: 14px 34px; border-radius: 999px; font-weight: 900; display: inline-block;">Unlock the sale</a>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Warm: Birthday",
        """
        <div style="font-family: __FONT__; max-width: 560px; margin: 0 auto; background: linear-gradient(180deg, #fff7ed 0%, #fff1f2 100%); border: 1px solid #fecdd3; border-radius: 24px; padding: 40px 34px; text-align: center; box-shadow: 0 12px 28px rgba(244, 114, 182, 0.08);">
            <div style="font-size: 48px; line-height: 1;">Cake</div>
            <h1 style="margin: 16px 0 0 0; color: #be185d; font-size: 32px; line-height: 1.1; font-weight: 900;">Happy Birthday, {{first_name}}</h1>
            <p style="margin: 14px 0 0 0; color: #831843; font-size: 16px; line-height: 1.7;">A thoughtful, warm layout with a gift code and enough space to let the message breathe.</p>
            <div style="background: #ffffff; border: 2px dashed #f9a8d4; border-radius: 16px; padding: 18px 24px; margin: 28px 0;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; color: #db2777;">Gift code</div>
                <div style="margin-top: 8px; font-size: 26px; font-family: monospace; font-weight: 900; color: #be185d;">CAKE30OFF</div>
            </div>
            <a href="#" style="background: #be185d; color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 10px; font-weight: 800; display: inline-block;">Claim your surprise</a>
        </div>
        """,
    ),
    tmpl(
        "B2B: Meeting Request",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 34px 32px; color: #334155; line-height: 1.8;">
            <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.14em; color: #64748b;">Outreach</div>
            <h2 style="margin: 10px 0 0 0; color: #111827; font-size: 28px; line-height: 1.2;">A quick introduction for {{company}}</h2>
            <p style="margin: 16px 0 0 0; font-size: 16px;">Hi {{first_name}}, I noticed {{company}} is scaling quickly, and I wanted to reach out with a concise idea that could help your team move faster without adding complexity.</p>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px; margin: 22px 0;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b;">What we can cover</div>
                <div style="margin-top: 8px; color: #0f172a; font-size: 14px; line-height: 1.8;">1. Delivery improvements<br>2. Cleaner follow-up sequences<br>3. A safer send workflow</div>
            </div>
            <p style="margin: 0; font-size: 16px;">Would you be open to a short call on Thursday or Friday?</p>
            <p style="margin: 18px 0 0 0; font-size: 16px;">Best regards,<br><strong>{{sender_name}}</strong><br>{{sender_title}}</p>
            <a href="#" style="margin-top: 18px; display: inline-block; background: #111827; color: #ffffff; padding: 12px 22px; border-radius: 10px; text-decoration: none; font-weight: 800;">Schedule a time</a>
        </div>
        """,
    ),
    tmpl(
        "Win-back: Miss You",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 24px; overflow: hidden;">
            <div style="display: grid; grid-template-columns: 1fr 0.95fr; gap: 0;">
                <div style="padding: 38px 34px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff;">
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.16em; color: #94a3b8;">Re-engagement</div>
                    <h2 style="margin: 14px 0 0 0; font-size: 30px; line-height: 1.12; font-weight: 900;">We have added a few things since you last visited</h2>
                    <p style="margin: 14px 0 0 0; color: #cbd5e1; font-size: 16px; line-height: 1.7;">A softer win-back layout that feels personal without pushing too hard.</p>
                    <a href="#" style="margin-top: 22px; display: inline-block; background: #ffffff; color: #0f172a; padding: 13px 22px; border-radius: 999px; text-decoration: none; font-weight: 800;">Take another look</a>
                </div>
                <div style="padding: 38px 30px; background: #ffffff; color: #334155;">
                    <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 16px; padding: 18px; margin-bottom: 14px;">
                        <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #2563eb;">New since you left</div>
                        <div style="margin-top: 8px; font-size: 15px; font-weight: 800; color: #0f172a;">Cleaner UI, smarter pacing, faster recovery.</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px; margin-bottom: 14px;">
                        <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b;">Offer</div>
                        <div style="margin-top: 8px; font-size: 26px; font-weight: 900; color: #0f172a;">BACKFORGOOD</div>
                    </div>
                    <p style="margin: 0; color: #64748b; font-size: 14px; line-height: 1.7;">If the timing is not right, this is still a polished way to remind people what they are missing.</p>
                </div>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Alert: Failed Payment",
        """
        <div style="font-family: __FONT__; max-width: 560px; margin: 0 auto; background: #ffffff; border: 1px solid #fee2e2; border-radius: 20px; overflow: hidden; box-shadow: 0 12px 28px rgba(127, 29, 29, 0.08);">
            <div style="padding: 26px 30px; background: linear-gradient(135deg, #dc2626 0%, #7f1d1d 100%); color: #ffffff;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.16em; opacity: 0.95;">Payment alert</div>
                <h2 style="margin: 10px 0 0 0; font-size: 24px; line-height: 1.2;">A payment did not go through</h2>
            </div>
            <div style="padding: 30px; color: #334155; line-height: 1.7;">
                <p style="margin: 0 0 18px 0;">Hi {{first_name}}, we were unable to process the latest charge on your account. The issue is often a card expiry or an authorization limit.</p>
                <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 16px; padding: 18px; margin-bottom: 22px;">
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #b91c1c;">Why this matters</div>
                    <div style="margin-top: 8px; color: #7f1d1d; font-size: 14px; line-height: 1.8;">Access may pause if the payment issue is not resolved by {{date}}.</div>
                </div>
                <div style="text-align: center;">
                    <a href="#" style="background: #111827; color: #ffffff; padding: 13px 24px; text-decoration: none; border-radius: 10px; font-weight: 800; display: inline-block;">Update payment method</a>
                </div>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Internal: Town Hall",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 22px; overflow: hidden; box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);">
            <div style="padding: 32px; background: linear-gradient(135deg, #eff6ff 0%, #eef2ff 100%); border-bottom: 1px solid #e2e8f0;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.16em; color: #64748b;">Internal update</div>
                <h2 style="margin: 12px 0 0 0; font-size: 28px; color: #111827; line-height: 1.15;">Quarterly town hall</h2>
                <p style="margin: 12px 0 0 0; color: #475569; font-size: 15px; line-height: 1.7;">A clean announcement for the team with the key details in one clear place.</p>
            </div>
            <div style="padding: 30px 32px; color: #334155; line-height: 1.7;">
                <div style="display: grid; gap: 14px; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-bottom: 22px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px;"><div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b;">Time</div><div style="margin-top: 8px; color: #0f172a; font-size: 16px; font-weight: 800;">10:30 AM EST</div></div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px;"><div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b;">Location</div><div style="margin-top: 8px; color: #0f172a; font-size: 16px; font-weight: 800;">Main room and Zoom</div></div>
                </div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; border-radius: 16px; padding: 18px; margin-bottom: 22px;">
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #2563eb;">Agenda</div>
                    <div style="margin-top: 8px; color: #475569; font-size: 14px; line-height: 1.8;">1. Product roadmap<br>2. Q and A<br>3. Team milestones</div>
                </div>
                <div style="text-align: center;">
                    <a href="#" style="background: #2563eb; color: #ffffff; padding: 13px 24px; text-decoration: none; border-radius: 10px; font-weight: 800; display: inline-block;">Add to calendar</a>
                </div>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Modern: Product Spotlight",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 24px; overflow: hidden; box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);">
            <div style="padding: 38px 34px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: #ffffff;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.16em; color: #94a3b8;">Spotlight</div>
                <h1 style="margin: 12px 0 0 0; font-size: 32px; line-height: 1.1; font-weight: 900;">A product story with more breathing room</h1>
                <p style="margin: 14px 0 0 0; color: #cbd5e1; font-size: 16px; line-height: 1.7;">This layout gives your launch the right hierarchy: one headline, one supporting message, and a single clear action.</p>
            </div>
            <div style="padding: 32px; color: #334155;">
                <div style="display: grid; gap: 14px; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-bottom: 22px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px;"><div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b;">Speed</div><div style="margin-top: 8px; color: #0f172a; font-size: 18px; font-weight: 900;">Faster setup</div></div>
                    <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 16px; padding: 18px;"><div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #2563eb;">Control</div><div style="margin-top: 8px; color: #0f172a; font-size: 18px; font-weight: 900;">Safer pacing</div></div>
                </div>
                <p style="margin: 0 0 22px 0; font-size: 16px; line-height: 1.7;">Hi {{first_name}}, the new release is built to keep the entire workflow more measured and easier to trust.</p>
                <a href="#" style="background: #2563eb; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 999px; font-weight: 800; display: inline-block;">See the product in action</a>
            </div>
        </div>
        """,
    ),
    tmpl(
        "Luxury: Showcase",
        """
        <div style="font-family: __FONT__; max-width: 640px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 28px; padding: 42px 32px; text-align: center; box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);">
            <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.2em; color: #64748b;">Collection</div>
            <h1 style="margin: 14px 0 0 0; color: #111827; font-size: 34px; line-height: 1.1; font-weight: 400;">A refined showcase for the latest drop</h1>
            <p style="margin: 14px 0 0 0; color: #6b7280; font-size: 16px; line-height: 1.8;">Use this layout when the message should feel editorial, premium, and intentionally spacious.</p>
            <div style="display: grid; gap: 14px; grid-template-columns: repeat(3, minmax(0, 1fr)); margin: 28px 0;">
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px; text-align: left;"><div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">One</div><div style="margin-top: 8px; color: #0f172a; font-size: 16px; font-weight: 800;">Editorial layout</div></div>
                <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 16px; padding: 18px; text-align: left;"><div style="font-size: 12px; color: #2563eb; text-transform: uppercase; letter-spacing: 0.08em;">Two</div><div style="margin-top: 8px; color: #0f172a; font-size: 16px; font-weight: 800;">Strong hierarchy</div></div>
                <div style="background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 16px; padding: 18px; text-align: left;"><div style="font-size: 12px; color: #7c3aed; text-transform: uppercase; letter-spacing: 0.08em;">Three</div><div style="margin-top: 8px; color: #0f172a; font-size: 16px; font-weight: 800;">Simple CTA</div></div>
            </div>
            <a href="#" style="display: inline-block; background: #111827; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 10px; font-weight: 800;">Explore the collection</a>
        </div>
        """,
    ),
]


PLACEHOLDER_REPLACEMENTS = {
    "[Name]": "{{first_name}}",
    "[First Name]": "{{first_name}}",
    "[Company]": "{{company}}",
    "[Your Name]": "{{sender_name}}",
    "[Your Title]": "{{sender_title}}",
}

COMPLIANCE_FOOTER = '''
<div style="margin-top: 26px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 12px; line-height: 1.7; color: #64748b; text-align: center;">
    You are receiving this email because you subscribed to updates.
    <br>
    <a href="{{unsubscribe_link}}" style="color: #2563eb; text-decoration: none;">Unsubscribe</a> |
    <a href="{{preferences_link}}" style="color: #2563eb; text-decoration: none;">Manage preferences</a>
</div>
'''


def normalize_template_html(html):
    normalized = html or ""
    for old, new in PLACEHOLDER_REPLACEMENTS.items():
        normalized = normalized.replace(old, new)
    if "{{unsubscribe_link}}" not in normalized:
        normalized += COMPLIANCE_FOOTER

    return f'<div class="template-wrapper" style="background-color: #f8fafc; padding: 40px 0; min-height: 100%;">{normalized}</div>'


ALL_TEMPLATES = templates + additional_templates


def generate_system_templates(data_dir=None):
    if not data_dir:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    templates_dir = os.path.join(data_dir, 'templates')
    os.makedirs(templates_dir, exist_ok=True)

    for filename in os.listdir(templates_dir):
        if filename.startswith('template_') and filename.endswith('.json'):
            try:
                os.remove(os.path.join(templates_dir, filename))
            except OSError:
                pass

    for i, template in enumerate(ALL_TEMPLATES):
        payload = {
            "name": template["name"],
            "html": normalize_template_html(template.get("html", "")),
        }
        filepath = os.path.join(templates_dir, f'template_{i}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=4)


if __name__ == '__main__':
    generate_system_templates()
    print(f"Generated {len(ALL_TEMPLATES)} preset templates in data/templates/")
