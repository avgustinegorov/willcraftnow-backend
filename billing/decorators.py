def register_discount_rule():
    from billing.discount_rule.discount_rule import discount_rules

    def _discount_rule_class_wrapper(discount_rule_class):
        discount_rules.register(discount_rule_class)
        return discount_rule_class

    return _discount_rule_class_wrapper
