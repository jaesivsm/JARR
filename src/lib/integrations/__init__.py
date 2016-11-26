from lib.integrations.abstract import add_integration, dispatch
from lib.integrations.mercury import MercuryIntegration


add_integration(MercuryIntegration())


__all__ = ['dispatch']
