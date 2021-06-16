from assets.models import Asset


def run():
    for asset in Asset.objects.all():
        if not asset.asset_store.all():
            print("-" * 30)
            print(asset.user)
            print(asset, asset.id)
            asset.delete()
