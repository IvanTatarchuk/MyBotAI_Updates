import { userResolvers } from './userResolvers';
import { portfolioResolvers } from './portfolioResolvers';
import { transactionResolvers } from './transactionResolvers';
import { marketResolvers } from './marketResolvers';
import { subscriptionResolvers } from './subscriptionResolvers';

export const resolvers = {
  Query: {
    ...userResolvers.Query,
    ...portfolioResolvers.Query,
    ...transactionResolvers.Query,
    ...marketResolvers.Query,
    ...subscriptionResolvers.Query,
  },
  Mutation: {
    ...userResolvers.Mutation,
    ...portfolioResolvers.Mutation,
    ...transactionResolvers.Mutation,
    ...subscriptionResolvers.Mutation,
  },
  User: userResolvers.User,
  Portfolio: portfolioResolvers.Portfolio,
  Transaction: transactionResolvers.Transaction,
  Subscription: subscriptionResolvers.Subscription,
};