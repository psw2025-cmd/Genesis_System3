from fastapi import FastAPI
from fastapi.testclient import TestClient
from audit.middleware import global_exception_handler


def test_global_exception_handler():
    test_app = FastAPI()
    test_app.add_exception_handler(Exception, global_exception_handler)

    @test_app.get("/boom")
    def boom():
        raise RuntimeError("failure")

    client = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/boom")
    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert "failure" in data["error"]
