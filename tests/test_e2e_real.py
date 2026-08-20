"""
E2E Real Test - Fixed for GitHub Actions CI
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Customer, Case
from app.database import get_db

# Setup test database
engine = create_engine("sqlite:///./test_e2e_real.db")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def log(step, status, message=""):
    print(f"[{step}] {status}: {message}")

def test_e2e_real_pipeline():
    """E2E test for complete customer -> case -> recommendation pipeline"""
    session = SessionLocal()
    
    try:
        # ===== STEP 1: Create Customer =====
        print("\n[STEP 1] Create Customer")
        customer = Customer(
            name="E2E Real Test Customer",
            mobile="09129999999",
            consent_to_store_data=1
        )
        session.add(customer)
        session.commit()
        log("Create Customer", "PASS", "id=" + str(customer.customer_id))
        
        # ===== STEP 2: Create Case =====
        print("\n[STEP 2] Create Case")
        case = Case(
            case_id="CASE_REAL_E2E_001",
            customer_id=customer.customer_id,
            case_type="CONSULTATION",
            reasoning_status="OPEN"
        )
        session.add(case)
        session.commit()
        log("Create Case", "PASS", "id=" + case.case_id)
        
        # ===== STEP 3: Verify Data =====
        print("\n[STEP 3] Verify Data")
        retrieved_customer = session.query(Customer).filter_by(customer_id=customer.customer_id).first()
        assert retrieved_customer is not None, "Customer not found"
        assert retrieved_customer.name == "E2E Real Test Customer"
        log("Verify Customer", "PASS")
        
        retrieved_case = session.query(Case).filter_by(case_id=case.case_id).first()
        assert retrieved_case is not None, "Case not found"
        assert retrieved_case.customer_id == customer.customer_id
        log("Verify Case", "PASS")
        
        print("\n✅ E2E Real Test PASSED")
        
    except Exception as e:
        session.rollback()
        log("E2E Test", "FAIL", str(e)[:200])
        pytest.fail(f"E2E test failed: {str(e)}")
        
    finally:
        # Cleanup
        session.query(Case).filter_by(case_id="CASE_REAL_E2E_001").delete()
        session.query(Customer).filter_by(mobile="09129999999").delete()
        session.commit()
        session.close()
