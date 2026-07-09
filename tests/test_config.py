import os

from src.config import load_project_env


def test_load_project_env_reads_key_value_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "# comentario",
                "GOOGLE_CLOUD_PROJECT=projeto-teste",
                "BIGQUERY_MAX_BYTES_BILLED=\"123\"",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.delenv("BIGQUERY_MAX_BYTES_BILLED", raising=False)

    loaded = load_project_env(env_file)

    assert loaded == ["GOOGLE_CLOUD_PROJECT", "BIGQUERY_MAX_BYTES_BILLED"]
    assert os.environ["GOOGLE_CLOUD_PROJECT"] == "projeto-teste"
    assert os.environ["BIGQUERY_MAX_BYTES_BILLED"] == "123"


def test_load_project_env_preserves_existing_values(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("GOOGLE_CLOUD_PROJECT=arquivo\n", encoding="utf-8")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "ambiente")

    loaded = load_project_env(env_file)

    assert loaded == []
    assert os.environ["GOOGLE_CLOUD_PROJECT"] == "ambiente"
