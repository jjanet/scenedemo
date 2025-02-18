# # from datasets import load_dataset_builder
# #
# # ds_builder = load_dataset_builder("rotten_tomatoes")
# #
# #
# # print(ds_builder.info.description)
# import stat
#
# from src.datasets import load_dataset
# from src.datasets.arrow_dataset import Dataset as ArrowDataset
# # from src.datasets import Dataset
# import os
#
# #
# # output_dir = "./csv_demo_hf"
# # # dataset = load_dataset("csv", data_files="best_movie_ratings_features.csv")
# #
# #
# # os.chmod(output_dir,stat.S_IRWXU)
# # # from src.datasets import load_dataset
# ds = load_dataset("rotten_tomatoes", split="validation")
# ds.to_parquet(output_dir)
#
# import pandas as pd
#
# # 构造示例数据
# data = {
#     '姓名': ['艾丽丝', '鲍勃', '查理'],
#     '年龄': [30, 25, 35],
#     '城市': ['纽约', '洛杉矶', '芝加哥']
# }
# df = pd.DataFrame(data)
#
# # 将 DataFrame 写入本地 Parquet 文件
# df.to_parquet('data.parquet')
#
#
# # dataset.save_to_disk(os.path.join(output_dir, "dataset"))
#
# arrowDataset =load_dataset(os.path.join(output_dir, "dataset"))
# # arrowDataset.to_parquet(os.path.join(output_dir, "pq"))
# # print(ds)
#
import pyarrow as pa
import json

my_schema = pa.schema([
    pa.field('n_legs', pa.int64()),
    pa.field('animals', pa.string())],
    metadata = {"n_legs": "Number of legs per animal"})


serialized_schema = my_schema.serialize().to_pybytes()
print(serialized_schema)

# 将序列化后的string反序列化回schema对象
deserialized_schema = pa.ipc.read_schema(pa.py_buffer(serialized_schema))
print("----------")
print(deserialized_schema)

# 原始schema定义
my_schema = pa.schema([
    pa.field('n_legs', pa.int64()),
    pa.field('animals', pa.string())],
    metadata = {"n_legs": "Number of legs per animal"})

# 序列化为JSON
schema_dict = {
    'fields': [
        {
            'name': field.name,
            'type': str(field.type),
            'nullable': field.nullable
        } for field in my_schema
    ],
    'metadata': {k.decode(): v.decode() for k, v in my_schema.metadata.items()}
}
json_str = json.dumps(schema_dict, indent=2)

# 从JSON反序列化
loaded_dict = json.loads(json_str)

print(loaded_dict)
deserialized_schema = pa.schema([
    pa.field(field['name'], pa.type_for_alias(field['type']), field['nullable'])
    for field in loaded_dict['fields']
], metadata={k.encode(): v.encode() for k, v in loaded_dict['metadata'].items()})
print(deserialized_schema)

