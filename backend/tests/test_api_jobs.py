import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_job(client: AsyncClient):
    """Test creating a new job."""
    response = await client.post(
        "/jobs",
        json={
            "title": "Software Engineer",
            "job_text_raw": "We are looking for a Python developer with 3+ years of experience.",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Software Engineer"
    assert "job_id" in data


@pytest.mark.asyncio
async def test_list_jobs(client: AsyncClient):
    """Test listing jobs."""
    # Create a job first
    await client.post(
        "/jobs",
        json={"title": "Test Job", "job_text_raw": "Test description"},
    )

    response = await client.get("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_job(client: AsyncClient):
    """Test getting a specific job."""
    # Create a job first
    create_response = await client.post(
        "/jobs",
        json={"title": "Test Job", "job_text_raw": "Test description"},
    )
    job_id = create_response.json()["job_id"]

    response = await client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["title"] == "Test Job"


@pytest.mark.asyncio
async def test_get_job_not_found(client: AsyncClient):
    """Test getting a non-existent job."""
    response = await client.get("/jobs/non-existent-id")
    assert response.status_code == 404
