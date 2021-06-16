def ExclusiveOrderType(order_type):
    def wrap(f):
        def wrapped_f(self, *args, **kwargs):
            if self.__class__.__name__ == "WillOrder":
                order = self
            else:
                if not hasattr(self, "order"):
                    raise Exception("Instance has no attribute order!")
                order = self.order

            if order_type != order.order_type:
                raise Exception(
                    f"This method is only for order type {order_type} -- {f.__name__}"
                )

            return f(self, *args, **kwargs)

        return wrapped_f

    return wrap
