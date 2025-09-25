export const typeDefs = `#graphql
  scalar Date
  scalar JSON

  type User {
    id: ID!
    email: String!
    firstName: String!
    lastName: String!
    fullName: String!
    role: UserRole!
    subscriptionTier: SubscriptionTier!
    emailVerified: Boolean!
    twoFactorEnabled: Boolean!
    phoneNumber: String
    profileImage: String
    preferences: UserPreferences
    lastLoginAt: Date
    createdAt: Date!
    updatedAt: Date!
    portfolios: [Portfolio!]!
    currentSubscription: Subscription
  }

  type UserPreferences {
    defaultCurrency: String!
    timezone: String!
    notifications: NotificationSettings!
  }

  type NotificationSettings {
    email: Boolean!
    push: Boolean!
    priceAlerts: Boolean!
  }

  type Portfolio {
    id: ID!
    name: String!
    description: String
    holdings: JSON!
    totalValue: Float!
    totalCost: Float!
    totalProfitLoss: Float!
    totalProfitLossPercentage: Float!
    baseCurrency: String!
    performance: PortfolioPerformance
    riskMetrics: RiskMetrics
    isPublic: Boolean!
    publicUrl: String
    createdAt: Date!
    updatedAt: Date!
    transactions: [Transaction!]!
    user: User!
  }

  type PortfolioPerformance {
    day: Float
    week: Float
    month: Float
    quarter: Float
    year: Float
    allTime: Float
  }

  type RiskMetrics {
    volatility: Float
    sharpeRatio: Float
    beta: Float
    maxDrawdown: Float
    valueAtRisk: Float
  }

  type Transaction {
    id: ID!
    type: TransactionType!
    symbol: String!
    amount: Float!
    price: Float!
    total: Float!
    fee: Float!
    currency: String!
    exchange: String!
    exchangeTransactionId: String
    blockchainTxHash: String
    walletAddress: String
    metadata: JSON
    timestamp: Date!
    status: TransactionStatus!
    createdAt: Date!
    portfolio: Portfolio!
  }

  type Subscription {
    id: ID!
    planId: String!
    planName: String!
    price: Float!
    currency: String!
    billingPeriod: BillingPeriod!
    status: SubscriptionStatus!
    startDate: Date!
    endDate: Date
    nextBillingDate: Date!
    trialEndsAt: Date
    features: SubscriptionFeatures!
    usage: SubscriptionUsage!
  }

  type SubscriptionFeatures {
    maxPortfolios: Int!
    maxTransactions: Int!
    apiAccess: Boolean!
    advancedAnalytics: Boolean!
    aiPredictions: Boolean!
    automatedTrading: Boolean!
    prioritySupport: Boolean!
    whiteLabel: Boolean!
    customIntegrations: Boolean!
  }

  type SubscriptionUsage {
    portfolios: Int!
    transactions: Int!
    apiCalls: Int!
    lastResetDate: Date!
  }

  type MarketData {
    symbol: String!
    name: String!
    price: Float!
    change24h: Float!
    change24hPercent: Float!
    marketCap: Float!
    volume24h: Float!
    high24h: Float!
    low24h: Float!
    sparkline: [Float!]
    lastUpdated: Date!
  }

  type PricePrediction {
    symbol: String!
    predictions: [Prediction!]!
    confidence: Float!
    model: String!
    generatedAt: Date!
  }

  type Prediction {
    timestamp: Date!
    price: Float!
    lowEstimate: Float!
    highEstimate: Float!
    probability: Float!
  }

  type AuthPayload {
    token: String!
    user: User!
  }

  enum UserRole {
    USER
    ADMIN
    ENTERPRISE
  }

  enum SubscriptionTier {
    FREE
    STARTER
    PROFESSIONAL
    ENTERPRISE
  }

  enum TransactionType {
    BUY
    SELL
    TRANSFER_IN
    TRANSFER_OUT
    STAKING_REWARD
    AIRDROP
    FEE
  }

  enum TransactionStatus {
    PENDING
    COMPLETED
    FAILED
    CANCELLED
  }

  enum SubscriptionStatus {
    ACTIVE
    CANCELLED
    EXPIRED
    TRIAL
    PAST_DUE
  }

  enum BillingPeriod {
    MONTHLY
    QUARTERLY
    YEARLY
  }

  input RegisterInput {
    email: String!
    password: String!
    firstName: String!
    lastName: String!
  }

  input LoginInput {
    email: String!
    password: String!
    twoFactorCode: String
  }

  input CreatePortfolioInput {
    name: String!
    description: String
    baseCurrency: String
  }

  input UpdatePortfolioInput {
    name: String
    description: String
    baseCurrency: String
    isPublic: Boolean
  }

  input CreateTransactionInput {
    portfolioId: ID!
    type: TransactionType!
    symbol: String!
    amount: Float!
    price: Float!
    fee: Float
    currency: String!
    exchange: String!
    timestamp: Date!
    metadata: JSON
  }

  input UpdateUserInput {
    firstName: String
    lastName: String
    phoneNumber: String
    preferences: UserPreferencesInput
  }

  input UserPreferencesInput {
    defaultCurrency: String
    timezone: String
    notifications: NotificationSettingsInput
  }

  input NotificationSettingsInput {
    email: Boolean
    push: Boolean
    priceAlerts: Boolean
  }

  type Query {
    # User queries
    me: User
    user(id: ID!): User
    users(limit: Int, offset: Int): [User!]!

    # Portfolio queries
    portfolio(id: ID!): Portfolio
    portfolios(userId: ID): [Portfolio!]!
    publicPortfolio(publicUrl: String!): Portfolio

    # Transaction queries
    transaction(id: ID!): Transaction
    transactions(portfolioId: ID!, limit: Int, offset: Int): [Transaction!]!

    # Market data queries
    marketData(symbols: [String!]!): [MarketData!]!
    topCryptocurrencies(limit: Int): [MarketData!]!
    searchCryptocurrencies(query: String!): [MarketData!]!

    # AI predictions
    pricePrediction(symbol: String!, timeframe: String!): PricePrediction

    # Subscription queries
    availablePlans: [SubscriptionPlan!]!
    mySubscription: Subscription
  }

  type Mutation {
    # Auth mutations
    register(input: RegisterInput!): AuthPayload!
    login(input: LoginInput!): AuthPayload!
    logout: Boolean!
    refreshToken: AuthPayload!
    verifyEmail(token: String!): Boolean!
    requestPasswordReset(email: String!): Boolean!
    resetPassword(token: String!, newPassword: String!): Boolean!
    enable2FA: String!
    disable2FA(code: String!): Boolean!

    # User mutations
    updateUser(input: UpdateUserInput!): User!
    deleteAccount(password: String!): Boolean!

    # Portfolio mutations
    createPortfolio(input: CreatePortfolioInput!): Portfolio!
    updatePortfolio(id: ID!, input: UpdatePortfolioInput!): Portfolio!
    deletePortfolio(id: ID!): Boolean!
    syncPortfolio(id: ID!): Portfolio!

    # Transaction mutations
    createTransaction(input: CreateTransactionInput!): Transaction!
    updateTransaction(id: ID!, input: CreateTransactionInput!): Transaction!
    deleteTransaction(id: ID!): Boolean!
    importTransactions(portfolioId: ID!, csv: String!): [Transaction!]!

    # Subscription mutations
    createSubscription(planId: String!, paymentMethodId: String!): Subscription!
    updateSubscription(planId: String!): Subscription!
    cancelSubscription: Boolean!
    reactivateSubscription: Boolean!
  }

  type SubscriptionPlan {
    id: String!
    name: String!
    price: Float!
    currency: String!
    billingPeriod: BillingPeriod!
    features: SubscriptionFeatures!
  }
`;