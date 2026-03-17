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
    }
]

for i, template in enumerate(templates):
    with open(os.path.join(templates_dir, f'template_{i}.json'), 'w') as f:
        json.dump(template, f, indent=4)

print("Generated 15 preset templates in data/templates/")
