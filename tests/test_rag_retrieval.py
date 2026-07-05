"""Scenario 4: RAG retrieval returns style-appropriate context, and different
styles retrieve different chunks (proves the collection isn't just returning
the same top-k regardless of query)."""
import shutil
import pytest
from src.rag.vectorstore import seed_collections, get_client
from src.rag.retriever import retrieve_style_context, retrieve_remotion_api_context
from tests.mocks import make_mock_intent


@pytest.fixture(scope="module", autouse=True)
def _clean_test_db(tmp_path_factory):
    # use an isolated chroma path so tests don't depend on / pollute a real run
    import src.rag.vectorstore as vs
    test_db = str(tmp_path_factory.mktemp("chroma_test_db"))
    vs._DB_PATH = test_db
    yield
    shutil.rmtree(test_db, ignore_errors=True)


def test_style_context_differs_between_cinematic_and_upbeat():
    cinematic_ctx = retrieve_style_context(make_mock_intent("cinematic"))
    upbeat_ctx = retrieve_style_context(make_mock_intent("upbeat"))

    assert cinematic_ctx != upbeat_ctx
    assert any("cinematic" in c.lower() for c in cinematic_ctx)
    assert any("upbeat" in c.lower() for c in upbeat_ctx)


def test_remotion_api_context_is_nonempty_and_code_shaped():
    ctx = retrieve_remotion_api_context(make_mock_intent("cinematic"))
    assert len(ctx) > 0
    assert any("import" in c for c in ctx)
