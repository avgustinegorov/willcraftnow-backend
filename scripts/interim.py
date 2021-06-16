from content.models import TermsAndConditions, PrivacyPolicy


def run():

    tncs = TermsAndConditions.objects.all()
    for y in tncs:
        print(y.content)
    print(TermsAndConditions.objects.all())
    print(PrivacyPolicy.objects.latest("id").content)
