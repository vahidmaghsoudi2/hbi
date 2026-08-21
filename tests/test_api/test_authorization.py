def test_protected_endpoint_without_token(client):
    response = client.get("/api/v1/evidence")
    assert response.status_code in (401, 403)


def test_protected_endpoint_with_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/evidence", headers=headers)
    assert response.status_code in (401, 403)
