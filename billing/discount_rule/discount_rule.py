class AlreadyRegistered(Exception):
    pass


class DiscountRule(object):
    _discount_rule_slug_to_discount_rule_class = {
        # 'discount_rule_slug': discount_rule_class,
    }
    slug = None
    name = None

    def register(self, discount_rule_class):
        if discount_rule_class.slug in self._discount_rule_slug_to_discount_rule_class:
            raise AlreadyRegistered('The discount_rule %s is already registered' % discount_rule_class.slug)
        self._discount_rule_slug_to_discount_rule_class[discount_rule_class.slug] = discount_rule_class

    def slug_to_discount_rule_class(self, discount_rule_slug):
        """
        Get class of this discount_rule slug
        :param discount_rule_slug:
        :return: discount_rule_class
        """
        return self._discount_rule_slug_to_discount_rule_class[discount_rule_slug]

    def get_all_discount_rules(self):
        """
        Retrun tuple of (slug, cls) of all discount_rules
        :return:
        """
        return ((slug, cls) for slug, cls in self._discount_rule_slug_to_discount_rule_class.items())

    def get_all_discount_rules_name(self):
        """
        Retrun tuple of (slug, name) of all discount_rules
        :return:
        """
        return ((slug, cls.name) for slug, cls in self._discount_rule_slug_to_discount_rule_class.items())

    @classmethod
    def apply_discount(cls, user, invoice) -> None:
        """
        Apply invoice to this user
        :param user:
        :param invoice:
        :return: None
        """
        raise NotImplementedError

    @classmethod
    def can_user_have_access(cls, user, invoice) -> bool:
        """
        This function checks that user have access to this discount
        :param user:
        :param invoice:
        :return: True or False
        """
        raise NotImplementedError


discount_rules = DiscountRule()
