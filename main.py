# from datasets import load_dataset_builder
#
# ds_builder = load_dataset_builder("rotten_tomatoes")
#
#
# print(ds_builder.info.description)


from src.datasets import load_dataset
from src.datasets.arrow_dataset import Dataset as ArrowDataset
# from src.datasets import Dataset
import os


output_dir = "./csv_demo_hf"
dataset = load_dataset("csv", data_files="best_movie_ratings_features.csv")


# dataset.save_to_disk(os.path.join(output_dir, "dataset"))

# arrowDataset =load_dataset(os.path.join(output_dir, "dataset"))
# arrowDataset.to_parquet(os.path.join(output_dir, "pq"))
print(dataset)

