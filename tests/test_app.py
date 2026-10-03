def test_home_page_returns_200(client):

    response = client.get("/")

    assert response.status_code == 200

    assert b"HomePulse" in response.data


def test_home_page_contains_input_field(client):

    response = client.get("/")

    assert response.status_code == 200

    assert b'name="user_input"' in response.data

    assert b"Device name" in response.data


def test_user_input_is_echoed(client):

    response = client.post(
        "/echo_user_input",
        data={
            "user_input": "Raspberry Pi 5"
        }
    )

    assert response.status_code == 200

    assert b"Raspberry Pi 5" in response.data


def test_health_endpoint(client):

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"

    assert data["service"] == "HomePulse"


def test_metrics_endpoint(client):

    response = client.get(
        "/metrics"
    )

    assert response.status_code == 200

    assert (
        b"homepulse_http_requests_total"
        in response.data
    )


def test_analysis_api_without_results(
    client
):

    response = client.get(
        "/api/analysis"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert (
        data["status"]
        == "not_available"
    )
