import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pytest
from pydantic import BaseModel

from common.event_source import EventSource, EventSourceFileHandler


# Dummy Pydantic model for testing
class SampleModel(BaseModel):
    id: str
    value: int


@pytest.fixture
def temp_storage():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def handler(temp_storage, monkeypatch):
    h = EventSourceFileHandler()
    monkeypatch.setattr(h, "root_storage_dir", Path(temp_storage))
    return h


@pytest.fixture
def source(handler, monkeypatch):
    s = EventSource()
    monkeypatch.setattr(s.file_handler, "root_storage_dir", handler.root_storage_dir)
    return s


def test_register_data_model(handler):
    model = SampleModel(id="a", value=123)
    handler.register_data_model(model)
    assert handler._get_data_object_name(model) in handler.objects
    assert (handler.root_storage_dir / "SampleModel").exists()


def test_write_transform(handler):
    model = SampleModel(id="123", value=1)
    handler.write_transform("id", model)
    path = handler.root_storage_dir / "SampleModel" / "staging.csv"
    assert path.exists()
    df = pd.read_csv(path, header=None)
    assert df.shape[1] == 3  # created_at, pk, data


def test_does_staged_csv_exist(handler):
    model = SampleModel(id="123", value=1)
    assert not handler.does_staged_csv_exist(model)
    handler.write_transform("id", model)
    assert handler.does_staged_csv_exist(model)


def test_consolidate_file(handler):
    model = SampleModel(id="123", value=1)
    handler.write_transform("id", model)
    handler.consolidate_file(model)
    parquet_files = list((handler.root_storage_dir / "SampleModel").glob("*.parquet"))
    assert len(parquet_files) == 1
    assert not (handler.root_storage_dir / "SampleModel" / "staging.csv").exists()


def test_return_max_event_source_log(handler):
    model = SampleModel(id="123", value=1)
    handler.write_transform("id", model)
    handler.consolidate_file(model)

    retrieved = handler.return_max_event_source_log("id", model)
    assert isinstance(retrieved, SampleModel)
    assert retrieved.id == "123"
    assert retrieved.value == 1


def test_log_new_event(source):
    model = SampleModel(id="abc", value=5)
    source.log_new_event("id", model)

    parquet_files = list(
        (source.file_handler.root_storage_dir / "SampleModel").glob("*.parquet")
    )
    assert len(parquet_files) == 1

    df = pd.read_parquet(parquet_files[0])
    assert df["pk"].iloc[0] == "abc"

    # Write the same object again: should NOT duplicate
    source.log_new_event("id", model)
    df_new = pd.read_parquet(parquet_files[0])
    assert len(df_new) == 1  # No duplicate

    # Now change the model and log again
    model2 = SampleModel(id="abc", value=6)
    source.log_new_event("id", model2)
    df_latest = pd.read_parquet(parquet_files[0])
    assert len(df_latest) == 2


def test_are_objects_equal():
    a = SampleModel(id="x", value=10)
    b = SampleModel(id="x", value=10)
    c = SampleModel(id="x", value=20)
    assert EventSource.are_objects_equal("id", a, b)
    assert not EventSource.are_objects_equal("id", a, c)
