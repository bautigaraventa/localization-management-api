import pytest
import time
from unittest.mock import patch, MagicMock

from localization_management_api.supabase import queries


def setup_mock_supabase(mock_get_supabase, keys_data, translations_data_list):
    mock_supabase = MagicMock()
    mock_get_supabase.return_value = mock_supabase

    table = mock_supabase.table.return_value
    select = table.select.return_value

    select.eq.return_value.execute.return_value.data = keys_data
    select.execute.return_value.data = keys_data

    select.in_.return_value.eq.return_value.execute.side_effect = [
        MagicMock(data=translations) for translations in translations_data_list
    ]

    return mock_supabase


@pytest.mark.asyncio
@patch('localization_management_api.supabase.queries.get_supabase')
async def test_fetch_localizations_performance(mock_get_supabase):
    keys = [
        {"id": 1, "key": "greeting", "category": "welcome", "project_id": "sample_project_id"},
        {"id": 2, "key": "farewell", "category": "other", "project_id": "sample_project_id"}
    ]
    translations = [
        {"key_id": 1, "value": "Hello", "updated_at": "2025-05-05"},
        {"key_id": 2, "value": "Goodbye", "updated_at": "2025-05-05"}
    ]
    setup_mock_supabase(mock_get_supabase, keys, [translations])

    start = time.perf_counter()
    result = await queries.fetch_localizations("sample_project_id", "en")
    elapsed = time.perf_counter() - start

    assert isinstance(result, list)
    assert len(result) == 2
    assert elapsed < 1.0


@pytest.mark.asyncio
@patch('localization_management_api.supabase.queries.get_supabase')
async def test_fetch_all_localizations_performance(mock_get_supabase):
    keys = [
        {"id": 1, "key": "greeting", "category": "welcome"},
        {"id": 2, "key": "farewell", "category": "other"}
    ]
    translations = [
        {"key_id": 1, "value": "Hello", "updated_at": "2025-05-05"},
        {"key_id": 2, "value": "Goodbye", "updated_at": "2025-05-05"}
    ]
    setup_mock_supabase(mock_get_supabase, keys, [translations])

    start = time.perf_counter()
    result = await queries.fetch_all_localizations("en")
    elapsed = time.perf_counter() - start

    assert isinstance(result, list)
    assert len(result) == 2
    assert elapsed < 1.0


@pytest.mark.asyncio
@patch('localization_management_api.supabase.queries.get_supabase')
async def test_translation_completion_percentages(mock_get_supabase):
    keys = [{"id": 1}, {"id": 2}, {"id": 3}]
    translations_data_list = [
        [{"key_id": 1}, {"key_id": 2}],  # en: 2/3
        [{"key_id": 1}, {"key_id": 2}, {"key_id": 3}],  # es: 3/3
        [{"key_id": 1}]  # pt: 1/3
    ]
    setup_mock_supabase(mock_get_supabase, keys, translations_data_list)

    start = time.perf_counter()
    result = await queries.get_translation_completion(123)
    elapsed = time.perf_counter() - start

    assert isinstance(result, dict)
    assert result["project_id"] == 123
    assert result["completion"] == {
        "en": 66.67,
        "es": 100.0,
        "pt": 33.33
    }
    assert elapsed < 1.0


@pytest.mark.asyncio
@patch('localization_management_api.supabase.queries.get_supabase')
async def test_translation_completion_performance(mock_get_supabase):
    keys = [{"id": i} for i in range(1, 101)]
    translations_data_list = [
        [{"key_id": i} for i in range(1, 81)],
        [{"key_id": i} for i in range(1, 101)],
        [{"key_id": i} for i in range(1, 51)]
    ]
    setup_mock_supabase(mock_get_supabase, keys, translations_data_list)

    start = time.perf_counter()
    result = await queries.get_translation_completion(456)
    elapsed = time.perf_counter() - start

    assert isinstance(result, dict)
    assert result["project_id"] == 456
    assert result["completion"] == {
        "en": 80.0,
        "es": 100.0,
        "pt": 50.0
    }
    assert elapsed < 1.0