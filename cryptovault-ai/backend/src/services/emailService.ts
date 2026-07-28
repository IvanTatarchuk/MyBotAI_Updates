import sgMail from '@sendgrid/mail';
import { logger } from '../utils/logger';

sgMail.setApiKey(process.env.SENDGRID_API_KEY!);

interface EmailOptions {
  to: string;
  subject: string;
  template: string;
  data: any;
}

const templates: { [key: string]: (data: any) => string } = {
  welcome: (data) => `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #3b82f6; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background-color: #f3f4f6; }
        .button { display: inline-block; padding: 12px 24px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>Welcome to CryptoVault AI!</h1>
        </div>
        <div class="content">
          <h2>Hi ${data.name},</h2>
          <p>Thank you for joining CryptoVault AI - the most advanced cryptocurrency portfolio management platform.</p>
          <p>To get started, please verify your email address by clicking the button below:</p>
          <a href="${data.verificationLink}" class="button">Verify Email</a>
          <p>This link will expire in 24 hours.</p>
          <p>If you didn't create an account with us, you can safely ignore this email.</p>
          <p>Best regards,<br>The CryptoVault AI Team</p>
        </div>
        <div class="footer">
          <p>&copy; 2024 CryptoVault AI. All rights reserved.</p>
        </div>
      </div>
    </body>
    </html>
  `,

  'password-reset': (data) => `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #3b82f6; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background-color: #f3f4f6; }
        .button { display: inline-block; padding: 12px 24px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>Password Reset Request</h1>
        </div>
        <div class="content">
          <h2>Hi ${data.name},</h2>
          <p>We received a request to reset your password. Click the button below to create a new password:</p>
          <a href="${data.resetLink}" class="button">Reset Password</a>
          <p>This link will expire in 1 hour.</p>
          <p>If you didn't request a password reset, you can safely ignore this email.</p>
          <p>Best regards,<br>The CryptoVault AI Team</p>
        </div>
        <div class="footer">
          <p>&copy; 2024 CryptoVault AI. All rights reserved.</p>
        </div>
      </div>
    </body>
    </html>
  `,

  'subscription-confirmation': (data) => `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #3b82f6; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background-color: #f3f4f6; }
        .plan-details { background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>Subscription Confirmed!</h1>
        </div>
        <div class="content">
          <h2>Hi ${data.name},</h2>
          <p>Thank you for subscribing to CryptoVault AI ${data.planName}!</p>
          <div class="plan-details">
            <h3>Your Plan Details:</h3>
            <ul>
              <li><strong>Plan:</strong> ${data.planName}</li>
              <li><strong>Price:</strong> $${data.price}/${data.billingPeriod}</li>
              <li><strong>Next Billing Date:</strong> ${data.nextBillingDate}</li>
            </ul>
            <h3>What's Included:</h3>
            <ul>
              ${data.features.map((feature: string) => `<li>${feature}</li>`).join('')}
            </ul>
          </div>
          <p>You can manage your subscription anytime from your account settings.</p>
          <p>Best regards,<br>The CryptoVault AI Team</p>
        </div>
        <div class="footer">
          <p>&copy; 2024 CryptoVault AI. All rights reserved.</p>
        </div>
      </div>
    </body>
    </html>
  `,
};

export async function sendEmail(options: EmailOptions): Promise<void> {
  try {
    const html = templates[options.template](options.data);
    
    const msg = {
      to: options.to,
      from: process.env.EMAIL_FROM || 'noreply@cryptovault.ai',
      subject: options.subject,
      html,
    };

    await sgMail.send(msg);
    logger.info(`Email sent to ${options.to}: ${options.subject}`);
  } catch (error) {
    logger.error('Email sending error:', error);
    throw error;
  }
}