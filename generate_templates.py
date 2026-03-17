import os
import json

templates_dir = 'data/templates'
os.makedirs(templates_dir, exist_ok=True)

# Generate 15 varied HTML templates
templates = [
    {
        "name": "Welcome Email",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
    <h2 style="color: #3b82f6; text-align: center;">Welcome to Our Community!</h2>
    <p>Hi there,</p>
    <p>We are thrilled to have you here. Get ready to explore all our amazing features.</p>
    <div style="text-align: center; margin: 30px 0;">
        <a href="#" style="background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">Get Started</a>
    </div>
    <p style="color: #666; font-size: 12px; text-align: center;">If you have any questions, reply to this email.</p>
</div>'''
    },
    {
        "name": "Weekly Newsletter",
        "html": '''<div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 600px; margin: auto; background-color: #f9fafb; padding: 0;">
    <div style="background-color: #1e293b; color: white; padding: 20px; text-align: center;">
        <h1>Weekly Digest</h1>
    </div>
    <div style="padding: 20px;">
        <h3 style="color: #333;">Top Story of the Week</h3>
        <p style="color: #555; line-height: 1.6;">Here is a summary of the most important news from us this week. Change this text to your own story, add images, and engage your audience!</p>
        <button style="background: #e2e8f0; border: none; padding: 10px 15px; cursor: pointer;">Read More</button>
    </div>
    <div style="background-color: #e2e8f0; padding: 15px; text-align: center; font-size: 12px; color: #64748b;">
        © 2026 Company Name. All rights reserved.
    </div>
</div>'''
    },
    {
        "name": "Product Launch",
        "html": '''<div style="font-family: Arial, sans-serif; text-align: center; padding: 40px 20px; max-width: 600px; margin: auto;">
    <img src="https://via.placeholder.com/600x200" alt="Product Reveal" style="max-width: 100%; border-radius: 8px;" />
    <h1 style="color: #111827; margin-top: 30px;">Introducing Our New Product</h1>
    <p style="color: #4b5563; font-size: 16px; margin-bottom: 30px;">It's finally here! Discover the revolutionary features of our latest release.</p>
    <a href="#" style="display: inline-block; background-color: #10b981; color: white; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-size: 18px; font-weight: bold;">Buy Now - 20% Off</a>
</div>'''
    },
    {
        "name": "Event Invitation",
        "html": '''<div style="background: #ffffff; border: 2px dashed #3b82f6; padding: 30px; max-width: 500px; margin: auto; font-family: sans-serif;">
    <h2 style="color: #1e40af; text-align: center;">You're Invited!</h2>
    <p style="text-align: center; font-size: 16px;">Join us for an exclusive VIP event this Friday at 8 PM.</p>
    <div style="background: #eff6ff; padding: 20px; margin-top: 20px; text-align: center; border-radius: 8px;">
        <h3 style="margin: 0;">Online Webinar</h3>
        <p>Save the Date: March 25, 2026</p>
    </div>
    <p style="text-align: center; margin-top: 30px;"><a href="#" style="color: #3b82f6; font-weight: bold;">RSVP Here →</a></p>
</div>'''
    },
    {
        "name": "Abandoned Cart",
        "html": '''<div style="max-width: 600px; margin: auto; font-family: Arial, sans-serif; padding: 20px; border-top: 5px solid #ef4444;">
    <h2>Wait! You forgot something...</h2>
    <p>We saved your cart for you. Don't miss out on these great items before they sell out.</p>
    <br>
    <a href="#" style="background: #ef4444; color: #fff; padding: 12px 20px; text-decoration: none; font-weight: bold; border-radius: 4px;">Return to Checkout</a>
</div>'''
    },
    {
        "name": "Thank You / Purchase Confirmation",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px; background: #fdfdfd; border: 1px solid #eaeaea;">
    <h2 style="color: #10b981;">Thank you for your purchase!</h2>
    <p>We have successfully processed your order <strong>#123456</strong>.</p>
    <hr style="border: none; border-top: 1px solid #eaeaea; margin: 20px 0;">
    <p style="color: #666;">We will notify you when your items ship. If you have any questions, please contact our support team.</p>
</div>'''
    },
    {
        "name": "Password Reset",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto; padding: 30px; text-align: center;">
    <h2>Password Reset Request</h2>
    <p style="color: #555; margin-bottom: 25px;">You requested a password reset. Click the button below to choose a new password.</p>
    <a href="#" style="background: #2563eb; color: #fff; padding: 12px 25px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
    <p style="font-size: 12px; color: #999; margin-top: 20px;">If you did not request this, please ignore this email.</p>
</div>'''
    },
    {
        "name": "Special Offer / Discount",
        "html": '''<div style="font-family: sans-serif; max-width: 600px; margin: auto; text-align: center; background: #000; color: #fff; padding: 40px;">
    <h1 style="color: #fbbf24; font-size: 48px; margin: 0;">50% OFF</h1>
    <h3 style="margin-top: 10px;">End of Season Sale</h3>
    <p style="font-size: 18px; margin: 20px 0;">Use code <strong>SAVE50</strong> at checkout.</p>
    <a href="#" style="background: #fbbf24; color: #000; padding: 15px 30px; text-decoration: none; font-weight: bold; font-size: 18px;">Shop Now</a>
</div>'''
    },
    {
        "name": "Feedback Request",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px; border: 1px solid #ccc; border-radius: 8px;">
    <h2>How did we do?</h2>
    <p>We'd love to hear your thoughts about your recent experience with us. It only takes a minute!</p>
    <div style="text-align: center; margin-top: 20px;">
        <a href="#" style="background: #10b981; color: #fff; padding: 12px 20px; text-decoration: none; border-radius: 4px; margin: 0 5px;">Good 👍</a>
        <a href="#" style="background: #ef4444; color: #fff; padding: 12px 20px; text-decoration: none; border-radius: 4px; margin: 0 5px;">Bad 👎</a>
    </div>
</div>'''
    },
    {
        "name": "System Status Update",
        "html": '''<div style="font-family: monospace; max-width: 600px; margin: auto; padding: 20px; background: #1e1e1e; color: #d4d4d4;">
    <h2 style="color: #fbbf24;">[System Alert] Maintenance Scheduled</h2>
    <p>We will be performing routine maintenance on our servers.</p>
    <ul>
        <li>Date: Saturday, March 20</li>
        <li>Time: 02:00 AM - 04:00 AM UTC</li>
        <li>Impact: Brief downtime (~15 mins)</li>
    </ul>
    <p style="color: #9cdcfe;">Thank you for your patience.</p>
</div>'''
    },
    {
        "name": "Job Application Received",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
    <h2 style="color: #3b82f6;">Application Received</h2>
    <p>Hi,</p>
    <p>Thank you for applying for the open position at our company. Our team will review your application and get back to you within 3-5 business days.</p>
    <p>Best Regards,<br>The Hiring Team</p>
</div>'''
    },
    {
        "name": "Happy Birthday",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; text-align: center; padding: 40px; background-color: #fce7f3; border-radius: 12px;">
    <h1 style="color: #be185d;">🎉 Happy Birthday! 🎂</h1>
    <p style="color: #831843; font-size: 18px;">Wishing you a fantastic day filled with joy and laughter.</p>
    <p style="color: #9d174d;">As a special gift, here is a 30% discount code: <strong>BDAY30</strong></p>
    <a href="#" style="display: inline-block; background-color: #be185d; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; margin-top: 20px;">Claim Gift</a>
</div>'''
    },
    {
        "name": "Refer a Friend",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px; border: 1px solid #e5e7eb; border-radius: 8px; text-align: center;">
    <h2 style="color: #4f46e5;">Love our service? Share it!</h2>
    <p>Invite your friends and you both get $10 credit when they sign up.</p>
    <div style="background: #f3f4f6; padding: 15px; font-size: 20px; font-weight: bold; letter-spacing: 2px; margin: 20px 0;">
        REF123XYZ
    </div>
    <a href="#" style="background: #4f46e5; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px;">Share unique link</a>
</div>'''
    },
    {
        "name": "Account Suspension Warning",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px; border-left: 5px solid #dc2626; background: #fef2f2;">
    <h2 style="color: #dc2626;">Action Required: Payment Failed</h2>
    <p>We were unable to process your last payment. Your account will be suspended in 3 days if the issue is not resolved.</p>
    <a href="#" style="background: #dc2626; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 10px;">Update Payment Method</a>
</div>'''
    },
    {
        "name": "Simple Text Style",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; color: #333; line-height: 1.5;">
    <p>Hi [Name],</p>
    <p>I just wanted to reach out and see if you had a moment to catch up next week regarding the new project.</p>
    <p>Let me know what time works best for you.</p>
    <p>Best,<br>Your Name</p>
</div>'''
    },
    {
        "name": "App Update / Feature Release",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px; border: 1px solid #e2e8f0; border-top: 5px solid #8b5cf6;">
    <h2 style="color: #6d28d9; text-align: center;">Version 2.0 is Here! 🚀</h2>
    <p style="color: #475569;">We've been working hard to bring you the most requested features. Update your app today to get access to:</p>
    <ul style="color: #475569; line-height: 1.6;">
        <li>Dark Mode support across all devices</li>
        <li> lightning-fast performance improvements</li>
        <li>New integration plugins</li>
    </ul>
    <div style="text-align: center; margin-top: 30px;">
        <a href="#" style="background: #8b5cf6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Download Update</a>
    </div>
</div>'''
    },
    {
        "name": "Review Request",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 40px 20px; text-align: center; background: #fafafa; border-radius: 8px;">
    <h2>Enjoying your purchase?</h2>
    <p style="color: #666; font-size: 16px;">Your feedback helps us create better products for everyone. Could you take 60 seconds to leave us a review?</p>
    <div style="margin: 30px 0;">
        <span style="font-size: 32px; color: #fbbf24; cursor: pointer;">★★★★★</span>
    </div>
    <a href="#" style="background: #111827; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; font-weight: bold;">Leave a Review</a>
</div>'''
    },
    {
        "name": "Subscription Renewal Warning",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px; border-left: 5px solid #f59e0b; background: #fffbeb;">
    <h2 style="color: #d97706;">Your Subscription is Expiring Soon</h2>
    <p style="color: #78350f;">Hi there,</p>
    <p style="color: #78350f;">Just a quick reminder that your annual subscription will renew automatically on <strong>March 30, 2026</strong>.</p>
    <p style="color: #78350f;">No action is required to continue enjoying our services. If you wish to make changes to your plan, click below.</p>
    <a href="#" style="display: inline-block; margin-top: 15px; background: #d97706; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Manage Subscription</a>
</div>'''
    },
    {
        "name": "Cyber Monday Mega Sale",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; text-align: center; background: linear-gradient(135deg, #0f172a, #1e293b); color: white; padding: 50px 20px;">
    <h3 style="color: #38bdf8; text-transform: uppercase; letter-spacing: 2px;">Cyber Monday Starts Now</h3>
    <h1 style="font-size: 54px; margin: 10px 0; color: #fff;">UP TO 70% OFF</h1>
    <p style="color: #94a3b8; font-size: 18px; margin-bottom: 30px;">Our biggest sale of the year is live. Stock is limited!</p>
    <a href="#" style="background: #38bdf8; color: #0f172a; padding: 16px 36px; text-decoration: none; font-weight: bold; font-size: 18px; border-radius: 50px;">SHOP THE SALE</a>
</div>'''
    },
    {
        "name": "Welcome Series: Day 2",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px;">
    <h2>Let's set up your profile</h2>
    <p>Welcome back! Let's get your account fully configured so you can get the most out of our platform.</p>
    <div style="background: #f1f5f9; padding: 20px; margin: 20px 0; border-radius: 8px;">
        <h3 style="margin-top: 0; color: #334155;">Step 1: Upload a Photo</h3>
        <p style="color: #64748b; font-size: 14px;">Profiles with photos get 3x more engagement.</p>
        <h3 style="color: #334155;">Step 2: Connect Socials</h3>
        <p style="color: #64748b; font-size: 14px;">Link your Twitter or LinkedIn for seamless sharing.</p>
    </div>
    <a href="#" style="color: #2563eb; font-weight: bold; text-decoration: none;">Go to Profile Settings &rarr;</a>
</div>'''
    },
    {
        "name": "Webinar Reminder (1 Hour Left)",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px; border: 2px solid #e0f2fe; background: #f0f9ff; text-align: center;">
    <h1 style="color: #0369a1;">We're starting in 1 hour!</h1>
    <p style="color: #0c4a6e; font-size: 18px;">Grab a coffee and get ready. The webinar room will open 10 minutes before start time.</p>
    <div style="margin: 30px 0;">
        <a href="#" style="background: #0ea5e9; color: white; padding: 15px 30px; text-decoration: none; font-weight: bold; font-size: 18px; border-radius: 8px;">Join the Web-Room</a>
    </div>
    <p style="color: #0369a1; font-size: 14px;">Need help logging in? <a href="#" style="color: #0284c7;">Click here</a>.</p>
</div>'''
    },
    {
        "name": "Daily Digest",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 0;">
    <div style="background: #fff; padding: 20px; border-bottom: 1px solid #eee;">
        <h2 style="margin: 0; color: #111;">Your Daily Digest</h2>
        <p style="color: #666; margin: 5px 0 0 0; font-size: 14px;">Tuesday, March 17th</p>
    </div>
    <div style="padding: 20px;">
        <h3 style="color: #222; margin-top: 0;">1. The Future of AI in Email Marketing</h3>
        <p style="color: #555; font-size: 15px;">Discover how automated personalization is driving click-through rates up by 40% across top industries...</p>
        <a href="#" style="color: #0066cc; font-size: 14px; text-decoration: none;">Read 5 min article</a>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        <h3 style="color: #222; margin-top: 0;">2. 10 Tips for Better Deliverability</h3>
        <p style="color: #555; font-size: 15px;">Are your emails hitting the spam folder? Check out our checklist for keeping your sender reputation pristine.</p>
        <a href="#" style="color: #0066cc; font-size: 14px; text-decoration: none;">Read 3 min article</a>
    </div>
</div>'''
    },
    {
        "name": "B2B Outreach / Lead Gen",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; color: #1f2937; line-height: 1.6;">
    <p>Hi [First Name],</p>
    <p>I noticed that [Company] is scaling rapidly, and I wanted to reach out because we recently helped [Competitor/Similar Company] achieve a 25% reduction in operational costs using our platform.</p>
    <p>Are you open to a quick 10-minute call this Thursday to see if we'd be a good fit for your current goals?</p>
    <p>No pressure either way.</p>
    <p>Best regards,<br><strong>[Your Name]</strong><br>[Your Title]<br><a href="#" style="color: #2563eb;">Schedule a Time</a></p>
</div>'''
    },
    {
        "name": "We Miss You (Win-back)",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 40px; text-align: center; border: 1px solid #f3f4f6;">
    <div style="font-size: 50px; margin-bottom: 20px;">🥺</div>
    <h2 style="color: #111827;">We miss you, [Name]!</h2>
    <p style="color: #4b5563; font-size: 16px; margin-bottom: 30px;">It's been a while since we last saw you. We've added a ton of new features and products we think you'll love.</p>
    <p style="color: #111827; font-weight: bold;">Come back today and get $20 off your next order.</p>
    <a href="#" style="display: inline-block; background: #000; color: #fff; padding: 14px 28px; text-decoration: none; font-weight: bold; margin-top: 20px;">Claim My $20</a>
</div>'''
    },
    {
        "name": "Internal Team Announcement",
        "html": '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px; background: #ffffff; border: 1px solid #d1d5db;">
    <div style="border-bottom: 2px solid #14b8a6; padding-bottom: 15px; margin-bottom: 20px;">
        <h2 style="color: #0f766e; margin: 0;">Company Update</h2>
        <span style="color: #6b7280; font-size: 13px;">INTERNAL TO ALL STAFF</span>
    </div>
    <p style="color: #374151;">Team,</p>
    <p style="color: #374151;">I am thrilled to announce that we have officially closed our Series B funding round! This is a massive milestone for all of us.</p>
    <p style="color: #374151;">Please join us for a town hall meeting tomorrow at 10 AM where the leadership team will discuss our next steps and roadmap for Q3.</p>
    <p style="color: #374151;">Thanks,<br>CEO</p>
</div>'''
    }
]

def generate_system_templates(data_dir=None):
    if not data_dir:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    templates_dir = os.path.join(data_dir, 'templates')
    os.makedirs(templates_dir, exist_ok=True)

    for i, template in enumerate(templates):
        filepath = os.path.join(templates_dir, f'template_{i}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=4)

if __name__ == '__main__':
    generate_system_templates()
    print("Generated 25 preset templates in data/templates/")
