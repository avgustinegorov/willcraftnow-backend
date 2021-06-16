import environ

env = environ.Env(
    # set casting, default value
    STRIPE_PUBLISHABLE=(str, "pk_test_pkDr9jtC4LlMven6BCSXWJjw"),
    STRIPE_SECRET=(str, "sk_test_UvPR1VeDVst4KabN6Gj1Bs9m"),
)
# reading .env file
environ.Env.read_env()

# Stripe Settings
STRIPE_PUBLISHABLE = env("STRIPE_PUBLISHABLE")
STRIPE_SECRET = env("STRIPE_SECRET")
