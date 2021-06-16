from core.tests.test_core import CoreTestCase


def run():
    core = CoreTestCase()
    user = core.setUp()
    for x in range(1, 50):
        attr = getattr(core, f"test_generate_will_{x}")
        attr()

    user.set_password("test")
