# PR #326 alignment to #325 tip

Aligned `app/api/routers/customers.py` with #325 head `6fd75fe` so same-mobile
identity uses only explicit `data.family_name` (no stored fallback). Logic was
already equivalent; comment/text unified to remove merge conflict.

Security tests retained on this branch:
- tests/test_identity_contract_mobile_family_name.py
- tests/test_staff_session_role_isolation.py
- tests/test_staff_admin_sale_persistence.py
- tests/test_staff_auth_consultation_sale_path.py

No force-push. No master change. No merge to master.
