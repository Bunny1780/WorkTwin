import pytest

from app.demo_imports import DEMO_ARTIFACTS, DEMO_EMPLOYEES, validate_demo_data


def test_demo_data_covers_all_sources_with_provenance_and_identity_mappings():
    validate_demo_data()

    identities = {
        (identity["provider"], identity["external_id"])
        for employee in DEMO_EMPLOYEES
        for identity in employee.identities
    }
    assert {artifact.source_type.split("_", 1)[0] for artifact in DEMO_ARTIFACTS} == {
        "slack",
        "github",
        "email",
    }
    assert all(artifact.author_identity in identities for artifact in DEMO_ARTIFACTS)
    assert all(artifact.source_uri and artifact.source_metadata for artifact in DEMO_ARTIFACTS)
    assert len(DEMO_ARTIFACTS) >= 12
    assert all(
        sum(
            artifact.author_identity in {(identity["provider"], identity["external_id"]) for identity in employee.identities}
            for artifact in DEMO_ARTIFACTS
        ) >= 4
        for employee in DEMO_EMPLOYEES
    )
    assert next(artifact for artifact in DEMO_ARTIFACTS if artifact.source_type == "email_thread").access_scope == "restricted"
    departed_employee = next(employee for employee in DEMO_EMPLOYEES if employee.employment_status == "departed")
    assert departed_employee.display_name == "Priya Nair"
    assert departed_employee.departed_at is not None
    assert next(artifact for artifact in DEMO_ARTIFACTS if artifact.source_type == "slack_thread").author_identity == (
        "slack",
        "U-PRIYA",
    )
    assert "Priya" in next(artifact for artifact in DEMO_ARTIFACTS if artifact.source_type == "github_pull_request").content
    assert "Priya" in next(artifact for artifact in DEMO_ARTIFACTS if artifact.source_type == "email_thread").content


def test_demo_data_validation_rejects_unknown_access_scope(monkeypatch):
    invalid_artifact = DEMO_ARTIFACTS[0].__class__(**{**DEMO_ARTIFACTS[0].__dict__, "access_scope": "private"})
    monkeypatch.setattr("app.demo_imports.DEMO_ARTIFACTS", (invalid_artifact, *DEMO_ARTIFACTS[1:]))

    with pytest.raises(ValueError, match="invalid access scope"):
        validate_demo_data()
