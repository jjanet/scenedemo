import itertools
from dataclasses import dataclass
from typing import List, Optional, Union

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq

from src import datasets
from src.datasets.table import table_cast


logger = datasets.utils.logging.get_logger(__name__)


@dataclass
class ParquetConfig(datasets.BuilderConfig):
    """BuilderConfig for Parquet."""

    batch_size: Optional[int] = None
    columns: Optional[List[str]] = None
    features: Optional[datasets.Features] = None
    filters: Optional[Union[ds.Expression, List[tuple], List[List[tuple]]]] = None

    def __post_init__(self):
        super().__post_init__()


class Parquet(datasets.ArrowBasedBuilder):
    BUILDER_CONFIG_CLASS = ParquetConfig

    def _info(self):
        if (
            self.config.columns is not None
            and self.config.features is not None
            and set(self.config.columns) != set(self.config.features)
        ):
            raise ValueError(
                "The columns and features argument must contain the same columns, but got ",
                f"{self.config.columns} and {self.config.features}",
            )
        return datasets.DatasetInfo(features=self.config.features)

    def _split_generators(self, dl_manager):
        """We handle string, list and dicts in datafiles"""
        if not self.config.data_files:
            raise ValueError(f"At least one data file must be specified, but got data_files={self.config.data_files}")
        dl_manager.download_config.extract_on_the_fly = True
        data_files = dl_manager.download_and_extract(self.config.data_files)
        splits = []
        for split_name, files in data_files.items():
            if isinstance(files, str):
                files = [files]
            # Use `dl_manager.iter_files` to skip hidden files in an extracted archive
            files = [dl_manager.iter_files(file) for file in files]
            # Infer features if they are stored in the arrow schema
            if self.info.features is None:
                for file in itertools.chain.from_iterable(files):
                    with open(file, "rb") as f:
                        self.info.features = datasets.Features.from_arrow_schema(pq.read_schema(f))
                    break
            splits.append(datasets.SplitGenerator(name=split_name, gen_kwargs={"files": files}))
        if self.config.columns is not None and set(self.config.columns) != set(self.info.features):
            self.info.features = datasets.Features(
                {col: feat for col, feat in self.info.features.items() if col in self.config.columns}
            )
        return splits

    def _cast_table(self, pa_table: pa.Table) -> pa.Table:
        if self.info.features is not None:
            # more expensive cast to support nested features with keys in a different order
            # allows str <-> int/float or str to Audio for example
            pa_table = table_cast(pa_table, self.info.features.arrow_schema)
        return pa_table

    def _generate_tables(self, files):
        if self.config.features is not None and self.config.columns is not None:
            if sorted(field.name for field in self.info.features.arrow_schema) != sorted(self.config.columns):
                raise ValueError(
                    f"Tried to load parquet data with columns '{self.config.columns}' with mismatching features '{self.info.features}'"
                )
        filter_expr = (
            pq.filters_to_expression(self.config.filters)
            if isinstance(self.config.filters, list)
            else self.config.filters
        )
        for file_idx, file in enumerate(itertools.chain.from_iterable(files)):
            with open(file, "rb") as f:
                parquet_fragment = ds.ParquetFileFormat().make_fragment(f)
                if parquet_fragment.row_groups:
                    batch_size = self.config.batch_size or parquet_fragment.row_groups[0].num_rows
                    try:
                        for batch_idx, record_batch in enumerate(
                            parquet_fragment.to_batches(
                                batch_size=batch_size,
                                columns=self.config.columns,
                                filter=filter_expr,
                                batch_readahead=0,
                                fragment_readahead=0,
                            )
                        ):
                            pa_table = pa.Table.from_batches([record_batch])
                            # Uncomment for debugging (will print the Arrow table size and elements)
                            # logger.warning(f"pa_table: {pa_table} num rows: {pa_table.num_rows}")
                            # logger.warning('\n'.join(str(pa_table.slice(i, 1).to_pydict()) for i in range(pa_table.num_rows)))
                            yield f"{file_idx}_{batch_idx}", self._cast_table(pa_table)
                    except ValueError as e:
                        logger.error(f"Failed to read file '{file}' with error {type(e)}: {e}")
                        raise
