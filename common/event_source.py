import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from pydantic import BaseModel


class EventSourceFileHandler:
    def __init__(self):
        self.objects = []
        self.root_storage_dir = Path("./storage")
        self.max_record_size = 500000
        self.data_frame_columns = {
            "created_at": "datetime64[ns]",
            "pk": "string",
            "data": "object",
        }

    @staticmethod
    def _get_data_object_name(data_object: BaseModel):
        """Get Name of Class from Object"""
        return data_object.__class__.__name__

    def create_storage_dir(self, new_dir):
        """Create Dir to Store Data In"""
        self.root_storage_dir.joinpath(new_dir).mkdir(parents=True, exist_ok=True)

    def register_data_model(self, data_object: BaseModel):
        """Register Files for New Data Model"""
        data_object_string = self._get_data_object_name(data_object)
        self.objects.append(data_object_string)
        self.create_storage_dir(data_object_string)

    def does_staged_csv_exist(self, data_object: BaseModel):
        """Does the Staged CSV already Exist?"""
        return self.root_storage_dir.joinpath(
            self._get_data_object_name(data_object), "staging.csv"
        ).exists()

    def consolidate_file(self, data_object):
        """Check if Staged CSV exists, if Yes - consolidate this into Parquet files. Parquet is partitioned 0, 1, ..."""
        if not self.does_staged_csv_exist(data_object):
            return

        staged_csv = pd.read_csv(
            self.root_storage_dir.joinpath(
                self._get_data_object_name(data_object), "staging.csv"
            ),
            header=None,
        )
        staged_csv.columns = list(self.data_frame_columns.keys())
        staged_csv = staged_csv.astype(self.data_frame_columns)

        current_parquet_files = list(
            self.root_storage_dir.joinpath(
                self._get_data_object_name(data_object)
            ).glob("*.parquet")
        )
        if current_parquet_files:
            current_parquet_files.sort(key=lambda x: str(x).split(".")[-2])
            max_file = current_parquet_files[-1]
            max_data_frame = pd.read_parquet(max_file)
            max_data_frame = max_data_frame.astype(self.data_frame_columns)
        else:
            max_data_frame = pd.DataFrame(
                {"created_at": [], "pk": [], "data": []}
            ).astype(self.data_frame_columns)
            max_file = self.root_storage_dir.joinpath(
                self._get_data_object_name(data_object), "0.parquet"
            )

        max_data_frame = pd.concat([max_data_frame, staged_csv], axis=0)
        max_data_frame.to_parquet(max_file)
        self.root_storage_dir.joinpath(
            self._get_data_object_name(data_object), "staging.csv"
        ).unlink()

    def write_transform(self, pk, data_object):
        """Write transformation to CSV"""
        self.create_storage_dir(self._get_data_object_name(data_object))
        data_frame = pd.DataFrame(
            {
                "created_at": datetime.now(),
                "pk": data_object.model_dump().get(pk),
                "data": json.dumps(data_object.model_dump()),
            },
            index=[1],
        )
        data_frame.to_csv(
            self.root_storage_dir.joinpath(
                self._get_data_object_name(data_object), "staging.csv"
            ),
            mode="a",
            header=False,
            index=False,
        )

    def return_max_event_source_log(self, pk, data_object):
        """Fetch the maximum event for a given data model and PK"""
        current_parquet_files = list(
            self.root_storage_dir.joinpath(
                self._get_data_object_name(data_object)
            ).glob("*.parquet")
        )
        if not current_parquet_files:
            return None
        current_parquet_files.sort(key=lambda x: str(x).split(".")[-2])
        pk_value = data_object.model_dump().get(pk)

        for file in current_parquet_files:
            data_frame = pd.read_parquet(file)
            data_frame = data_frame.astype(
                {"created_at": "object", "pk": "string", "data": "object"}
            )
            slice = data_frame[data_frame["pk"] == pk_value].sort_values(
                by="created_at", ascending=False
            )
            if slice.shape[0] >= 1:
                return data_object.__class__(**json.loads(slice.iloc[0].data))
        return None


class EventSource:
    def __init__(self):
        self.file_handler = EventSourceFileHandler()

    @staticmethod
    def are_objects_equal(pk, object_one, object_two):
        """Given a PK, compare 2 pydantic data objects and compare if they are identical or have changed"""
        object_one_keys = object_one.__class__.model_fields.keys()
        object_two_keys = object_two.__class__.model_fields.keys()
        assert pk in object_one_keys
        assert set(object_two_keys) == set(object_one_keys)

        dumped_object_one = object_one.model_dump()
        dumped_object_two = object_two.model_dump()

        assert dumped_object_one.get(pk) == dumped_object_two.get(pk)
        equals = []
        for key in [i for i in object_one_keys if i != pk]:
            equals.append(dumped_object_one.get(key) == dumped_object_two.get(key))
        return all(equals)

    def log_transform_to_file(self, pk, data_object):
        """Log PyDantic Transform"""
        self.file_handler.write_transform(pk, data_object)

    def consolidate_file(self, data_object):
        """Convert CSV to Parquet"""
        self.file_handler.consolidate_file(data_object)

    def source_consolidated(self, data_object):
        """Does the Staged CSV exist?"""
        return not self.file_handler.does_staged_csv_exist(data_object)

    def fetch_most_recent_record(self, pk, data_object):
        """Fetch the Most recent Record from Parquet"""
        return self.file_handler.return_max_event_source_log(pk, data_object)

    def log_new_event(self, pk, new_data_object):
        """Log a new event in Parquet."""
        if not self.source_consolidated(new_data_object):
            self.consolidate_file(new_data_object)

        latest_saved_object = self.fetch_most_recent_record(pk, new_data_object)
        if latest_saved_object is not None:
            if self.are_objects_equal(pk, new_data_object, latest_saved_object):
                return
        self.log_transform_to_file(pk, new_data_object)
        self.consolidate_file(new_data_object)
