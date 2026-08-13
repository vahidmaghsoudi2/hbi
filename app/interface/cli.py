"""
Simple CLI entry point for HBI Interface Layer
Usage examples (from project root):
    python -m app.interface.cli
"""
from app.database import SessionLocal, init_db
from app.interface.facades import (
    ProductFacade, CustomerFacade, CaseFacade,
    RecommendationFacade, InventoryFacade, SaleFacade
)

def main():
    print("=" * 50)
    print("HBI Interface Layer - CLI")
    print("=" * 50)

    init_db()
    db = SessionLocal()

    try:
        product_facade = ProductFacade(db)
        customer_facade = CustomerFacade(db)
        case_facade = CaseFacade(db)
        recommendation_facade = RecommendationFacade(db)
        inventory_facade = InventoryFacade(db)
        sale_facade = SaleFacade(db)

        print("\nFacades loaded successfully:")
        print("  - ProductFacade")
        print("  - CustomerFacade")
        print("  - CaseFacade")
        print("  - RecommendationFacade")
        print("  - InventoryFacade")
        print("  - SaleFacade")
        print("\nInterface Layer is ready.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
