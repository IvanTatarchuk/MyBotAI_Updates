import Stripe from 'stripe';
import { AppDataSource } from '../config/database';
import { User } from '../models/User';
import { Subscription, SubscriptionStatus, BillingPeriod } from '../models/Subscription';
import { logger } from '../utils/logger';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

export class StripeService {
  // Subscription plans
  static readonly PLANS = {
    starter: {
      monthly: 'price_starter_monthly',
      yearly: 'price_starter_yearly',
      features: {
        maxPortfolios: 3,
        maxTransactions: 1000,
        apiAccess: false,
        advancedAnalytics: true,
        aiPredictions: true,
        automatedTrading: false,
        prioritySupport: false,
        whiteLabel: false,
        customIntegrations: false,
      },
    },
    professional: {
      monthly: 'price_professional_monthly',
      yearly: 'price_professional_yearly',
      features: {
        maxPortfolios: 10,
        maxTransactions: 10000,
        apiAccess: true,
        advancedAnalytics: true,
        aiPredictions: true,
        automatedTrading: true,
        prioritySupport: true,
        whiteLabel: false,
        customIntegrations: false,
      },
    },
    enterprise: {
      monthly: 'price_enterprise_monthly',
      yearly: 'price_enterprise_yearly',
      features: {
        maxPortfolios: -1, // Unlimited
        maxTransactions: -1, // Unlimited
        apiAccess: true,
        advancedAnalytics: true,
        aiPredictions: true,
        automatedTrading: true,
        prioritySupport: true,
        whiteLabel: true,
        customIntegrations: true,
      },
    },
  };

  static async createCustomer(user: User): Promise<string> {
    try {
      const customer = await stripe.customers.create({
        email: user.email,
        name: user.fullName,
        metadata: {
          userId: user.id,
        },
      });

      return customer.id;
    } catch (error) {
      logger.error('Stripe create customer error:', error);
      throw error;
    }
  }

  static async createSubscription(
    userId: string,
    planId: string,
    paymentMethodId: string
  ): Promise<Subscription> {
    const userRepository = AppDataSource.getRepository(User);
    const subscriptionRepository = AppDataSource.getRepository(Subscription);

    try {
      const user = await userRepository.findOne({ where: { id: userId } });
      if (!user) throw new Error('User not found');

      // Create or get Stripe customer
      let customerId = user.stripeCustomerId;
      if (!customerId) {
        customerId = await this.createCustomer(user);
        user.stripeCustomerId = customerId;
        await userRepository.save(user);
      }

      // Attach payment method to customer
      await stripe.paymentMethods.attach(paymentMethodId, {
        customer: customerId,
      });

      // Set as default payment method
      await stripe.customers.update(customerId, {
        invoice_settings: {
          default_payment_method: paymentMethodId,
        },
      });

      // Create Stripe subscription
      const stripeSubscription = await stripe.subscriptions.create({
        customer: customerId,
        items: [{ price: planId }],
        payment_settings: {
          payment_method_types: ['card'],
          save_default_payment_method: 'on_subscription',
        },
        expand: ['latest_invoice.payment_intent'],
      });

      // Determine plan details
      const planDetails = this.getPlanDetails(planId);

      // Create subscription record
      const subscription = subscriptionRepository.create({
        userId: user.id,
        planId,
        planName: planDetails.name,
        price: planDetails.price,
        currency: 'USD',
        billingPeriod: planDetails.billingPeriod,
        status: this.mapStripeStatus(stripeSubscription.status),
        startDate: new Date(stripeSubscription.current_period_start * 1000),
        endDate: new Date(stripeSubscription.current_period_end * 1000),
        nextBillingDate: new Date(stripeSubscription.current_period_end * 1000),
        stripeCustomerId: customerId,
        stripeSubscriptionId: stripeSubscription.id,
        stripePaymentMethodId: paymentMethodId,
        features: planDetails.features,
        usage: {
          portfolios: 0,
          transactions: 0,
          apiCalls: 0,
          lastResetDate: new Date(),
        },
      });

      await subscriptionRepository.save(subscription);

      // Update user subscription tier
      user.subscriptionTier = planDetails.tier;
      await userRepository.save(user);

      logger.info(`Subscription created for user ${userId}: ${planId}`);

      return subscription;
    } catch (error) {
      logger.error('Create subscription error:', error);
      throw error;
    }
  }

  static async updateSubscription(
    subscriptionId: string,
    newPlanId: string
  ): Promise<Subscription> {
    const subscriptionRepository = AppDataSource.getRepository(Subscription);

    try {
      const subscription = await subscriptionRepository.findOne({
        where: { id: subscriptionId },
      });

      if (!subscription) throw new Error('Subscription not found');

      // Update Stripe subscription
      const stripeSubscription = await stripe.subscriptions.update(
        subscription.stripeSubscriptionId!,
        {
          items: [{
            id: (await stripe.subscriptions.retrieve(subscription.stripeSubscriptionId!))
              .items.data[0].id,
            price: newPlanId,
          }],
          proration_behavior: 'create_prorations',
        }
      );

      // Update plan details
      const planDetails = this.getPlanDetails(newPlanId);
      subscription.planId = newPlanId;
      subscription.planName = planDetails.name;
      subscription.price = planDetails.price;
      subscription.features = planDetails.features;

      await subscriptionRepository.save(subscription);

      logger.info(`Subscription updated: ${subscriptionId} to ${newPlanId}`);

      return subscription;
    } catch (error) {
      logger.error('Update subscription error:', error);
      throw error;
    }
  }

  static async cancelSubscription(subscriptionId: string): Promise<boolean> {
    const subscriptionRepository = AppDataSource.getRepository(Subscription);

    try {
      const subscription = await subscriptionRepository.findOne({
        where: { id: subscriptionId },
      });

      if (!subscription) throw new Error('Subscription not found');

      // Cancel at period end
      await stripe.subscriptions.update(subscription.stripeSubscriptionId!, {
        cancel_at_period_end: true,
      });

      subscription.status = SubscriptionStatus.CANCELLED;
      subscription.cancelledAt = new Date();

      await subscriptionRepository.save(subscription);

      logger.info(`Subscription cancelled: ${subscriptionId}`);

      return true;
    } catch (error) {
      logger.error('Cancel subscription error:', error);
      throw error;
    }
  }

  static async handleWebhook(event: Stripe.Event): Promise<void> {
    const subscriptionRepository = AppDataSource.getRepository(Subscription);

    try {
      switch (event.type) {
        case 'customer.subscription.updated':
        case 'customer.subscription.deleted':
          const subscription = event.data.object as Stripe.Subscription;
          
          const dbSubscription = await subscriptionRepository.findOne({
            where: { stripeSubscriptionId: subscription.id },
          });

          if (dbSubscription) {
            dbSubscription.status = this.mapStripeStatus(subscription.status);
            dbSubscription.endDate = new Date(subscription.current_period_end * 1000);
            
            if (event.type === 'customer.subscription.deleted') {
              dbSubscription.status = SubscriptionStatus.CANCELLED;
              dbSubscription.cancelledAt = new Date();
            }

            await subscriptionRepository.save(dbSubscription);
          }
          break;

        case 'invoice.payment_succeeded':
          const invoice = event.data.object as Stripe.Invoice;
          logger.info(`Payment succeeded for invoice: ${invoice.id}`);
          break;

        case 'invoice.payment_failed':
          const failedInvoice = event.data.object as Stripe.Invoice;
          
          const failedSubscription = await subscriptionRepository.findOne({
            where: { stripeCustomerId: failedInvoice.customer as string },
          });

          if (failedSubscription) {
            failedSubscription.status = SubscriptionStatus.PAST_DUE;
            await subscriptionRepository.save(failedSubscription);
          }

          logger.error(`Payment failed for invoice: ${failedInvoice.id}`);
          break;
      }
    } catch (error) {
      logger.error('Webhook handler error:', error);
      throw error;
    }
  }

  private static getPlanDetails(planId: string): any {
    const planMap: { [key: string]: any } = {
      price_starter_monthly: {
        name: 'Starter Monthly',
        price: 299,
        tier: 'STARTER',
        billingPeriod: BillingPeriod.MONTHLY,
        features: this.PLANS.starter.features,
      },
      price_starter_yearly: {
        name: 'Starter Yearly',
        price: 2990,
        tier: 'STARTER',
        billingPeriod: BillingPeriod.YEARLY,
        features: this.PLANS.starter.features,
      },
      price_professional_monthly: {
        name: 'Professional Monthly',
        price: 999,
        tier: 'PROFESSIONAL',
        billingPeriod: BillingPeriod.MONTHLY,
        features: this.PLANS.professional.features,
      },
      price_professional_yearly: {
        name: 'Professional Yearly',
        price: 9990,
        tier: 'PROFESSIONAL',
        billingPeriod: BillingPeriod.YEARLY,
        features: this.PLANS.professional.features,
      },
      price_enterprise_monthly: {
        name: 'Enterprise Monthly',
        price: 4999,
        tier: 'ENTERPRISE',
        billingPeriod: BillingPeriod.MONTHLY,
        features: this.PLANS.enterprise.features,
      },
      price_enterprise_yearly: {
        name: 'Enterprise Yearly',
        price: 49990,
        tier: 'ENTERPRISE',
        billingPeriod: BillingPeriod.YEARLY,
        features: this.PLANS.enterprise.features,
      },
    };

    return planMap[planId] || planMap.price_starter_monthly;
  }

  private static mapStripeStatus(stripeStatus: Stripe.Subscription.Status): SubscriptionStatus {
    const statusMap: { [key: string]: SubscriptionStatus } = {
      active: SubscriptionStatus.ACTIVE,
      canceled: SubscriptionStatus.CANCELLED,
      incomplete: SubscriptionStatus.EXPIRED,
      incomplete_expired: SubscriptionStatus.EXPIRED,
      past_due: SubscriptionStatus.PAST_DUE,
      trialing: SubscriptionStatus.TRIAL,
      unpaid: SubscriptionStatus.PAST_DUE,
    };

    return statusMap[stripeStatus] || SubscriptionStatus.EXPIRED;
  }

  static async createPaymentIntent(amount: number, currency: string = 'usd'): Promise<Stripe.PaymentIntent> {
    try {
      return await stripe.paymentIntents.create({
        amount: Math.round(amount * 100), // Convert to cents
        currency,
        automatic_payment_methods: {
          enabled: true,
        },
      });
    } catch (error) {
      logger.error('Create payment intent error:', error);
      throw error;
    }
  }

  static async createCheckoutSession(
    userId: string,
    planId: string,
    successUrl: string,
    cancelUrl: string
  ): Promise<string> {
    try {
      const session = await stripe.checkout.sessions.create({
        payment_method_types: ['card'],
        line_items: [
          {
            price: planId,
            quantity: 1,
          },
        ],
        mode: 'subscription',
        success_url: successUrl,
        cancel_url: cancelUrl,
        client_reference_id: userId,
      });

      return session.url!;
    } catch (error) {
      logger.error('Create checkout session error:', error);
      throw error;
    }
  }
}