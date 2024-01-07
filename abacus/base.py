"""Base classes (may helps to prevent circular import)."""


class AbacusError(Exception):
    """Custom error for this project."""


# FIXME: can use decimal.Decimal
Amount = int
