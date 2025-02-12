# from datasets import load_dataset_builder
#
# ds_builder = load_dataset_builder("rotten_tomatoes")
#
#
# print(ds_builder.info.description)


from src.datasets import load_dataset
dataset = load_dataset("csv", data_files="best_movie_ratings_features.csv")
print(dataset)

