import pytest
from app.models import Customer, Case
from app.database import SessionLocal

def test_e2e_real_pipeline():
    session = SessionLocal()
    try:
        # STEP 1: Create Customer with explicit customer_id to satisfy NOT NULL constraint
        customer = Customer(
            customer_id="CUST_E2E_001",
            name="E2E Real Test Customer",
            mobile="09129999999",
            consent_to_store_data=1
        )
        session.add(customer)
        session.commit()
        
        # STEP 2: Create Case
        case = Case(
            case_id="CASE_REAL_E2E_001",
            customer_id=customer.customer_id,
            case_type="CONSULTATION",
            reasoning_status="OPEN"
        )
        session.add(case)
        session.commit()
        
        assert customer.customer_id is not None
        
    except Exception as e:
        session.rollback()
        pytest.fail(f"E2E test failed: {str(e)}")
    finally:
        # Cleanup
        session.query(Case).filter_by(case_id="CASE_REAL_E2E_001").delete(synchronize_session=False)
        session.query(Customer).filter_by(mobile="09129999999").delete(synchronize_session=False)
        session.commit()
        session.close()
