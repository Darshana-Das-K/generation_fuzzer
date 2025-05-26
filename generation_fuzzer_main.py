import os
import yaml


from handle import handle_seq
from handle_meta import handle_meta
from conditionals_preprocessing import preprocess_kaitai_struct, dependency_order
from handle_instances import handle_instances
import os


def write_leaf_values_to_file(data_tree, output_directory):
    id = data_tree['meta']['id']
    file_extension = data_tree['meta'].get('file-extension', '')
    
    # Determine the file path
    filename = f"{id}.{file_extension}" if file_extension else f"{id}"
    filepath = os.path.join(output_directory, filename)
    
    with open(filepath, 'wb') as file:
        # Write the contents of 'expansion' field for each item in 'seq' to the file
        if 'seq' in data_tree:
            for item in data_tree['seq']:
                field_value = item.get('expansion')
                if field_value is not None:
                    file.write(field_value)
        # Write the contents of 'expansion' field for each item in 'instances' to the file
        if 'instances' in data_tree:
                    for item_key, item_value in data_tree['instances'].items():
                        pos = item_value.get('pos')
                        field_value = item_value.get('expansion')
                        if pos is not None and field_value is not None:
                            file.seek(pos)
                            file.write(field_value)
        return filepath
          #  value=''
          #  if repeat is not None:
            #    value= repeat_field(field_value,repeat)
            #    if value is not None:
             #       file.write(value)
           # else:
                #repeat_field(data_tree, output_directory, field_value, 1)
            #value = item.get('expansion')
            
def generate_binary(ksy_file, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    with open(ksy_file, 'r') as file:
        yaml_data = file.read()

    data_tree = yaml.safe_load(yaml_data)

    endianness, file_extension, file_id = handle_meta(data_tree['meta'])

    # Optional: dependency analysis (can be printed if needed)
    # dependency_graph = preprocess_kaitai_struct(data_tree['seq'])
    # ordered_list = dependency_order(dependency_graph)

    handle_seq(data_tree['seq'], endianness, data_tree, data_tree, 'data_tree')

    # Optional: Uncomment if instances should also be handled
    # handle_instances(data_tree['instances'], endianness, data_tree, data_tree, None)

    return write_leaf_values_to_file(data_tree, output_directory)