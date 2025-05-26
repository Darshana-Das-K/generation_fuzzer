from random_generate import random_based_on_size, random_based_on_type,convert_value_to_type, unpack_value_from_type
from pack_list import pack_list
from conditionals_preprocessing import preprocess_kaitai_struct, dependency_order
#from evaluate_condition import evaluate_condition
import random
import string
from handle_enum import handle_enum
from evaluate_size import evaluate_size
from find_user_defined_type import find_user_defined_type
from evaluate_value import max_value_for_type
#from handle_switch import handle_switch
from find_dict import find_dict
from evaluate_value import pack_value
from handle_valid import handle_valid, dot_operator_simple, evaluate_condition
import re
def add_value_to_node(item, value):
    item['expansion'] = value

def append_value_to_node(item, value):
    if 'expansion' not in item:
        item['expansion'] = b''
    item['expansion'] += value

def handle_field(field, endian, parent, root, parent_string):
    #print("The parent string is ",parent['seq'])
    endianness= '<' if endian == 'le' else '>'
    content = field.get('contents')
    field_type = field.get('type')
    size = evaluate_size(field.get('size', 0), root, endianness, parent, field)
    encoding = field.get('encoding')
    enum_name=field.get('enum')
    valid_value=field.get('valid')
    if content is not None:
        expansion = pack_list(content, '<' if endian == 'le' else '>')
    elif valid_value is not None:
         expansion = handle_valid(valid_value, field_type,parent,root,endianness,encoding)
    elif field_type:
        if enum_name:
            expansion=handle_enum(root,parent, enum_name, field_type, '<' if endian == 'le' else '>')
        else:
            expansion=handle_type(field,field_type,parent,endian,root,parent_string)
    else:
        expansion = random_based_on_size(size, endian)
    
    return expansion

# def handle_valid(valid_value, field_type, endianness, encoding="ASCII"):
#     if isinstance(valid_value, dict):
#         if 'min' in valid_value and 'max' in valid_value:
#             min_value = valid_value['min']
#             max_value = valid_value['max']
#             exp = random.randint(min_value, max_value)
#             return convert_value_to_type(exp, field_type, endianness, encoding)
#         elif 'min' in valid_value:
#             min_value = valid_value['min']
#             max_type = max_value_for_type(field_type)
#             exp = random.randint(min_value, max_type)  
#             return convert_value_to_type(exp, field_type, endianness, encoding)
#         elif 'max' in valid_value:
#             max_value = valid_value['max']
#             exp = random.randint(0, max_value)
#             return convert_value_to_type(exp, field_type, endianness, encoding)
#         elif 'eq' in valid_value:
#             eq_value = valid_value['eq']
#             return convert_value_to_type(eq_value, field_type, endianness, encoding)
#         elif 'any-of' in valid_value:
#             possible_values = valid_value['any-of']
#             if field_type == 'str':
#                 possible_values = valid_value['any-of']
#                 for i in range(len(possible_values)):
#                     if isinstance(possible_values[i], str) and possible_values[i].startswith('"') and possible_values[i].endswith('"'):
#                         possible_values[i] = possible_values[i][1:-1]
#                 selected_value = random.choice(possible_values)
#                 return convert_value_to_type(selected_value, field_type, endianness, encoding)
#             selected_value = random.choice(possible_values)
#             print(possible_values)
#             return convert_value_to_type(selected_value, field_type, endianness, encoding)
#         elif 'expr' in valid_value:
#             expr = valid_value['expr']
#             if isinstance(expr, str):
#                 max_type=max_value_for_type(field_type)
#                 max_attempts = 1000
#                 for _ in range(max_attempts):
#                     try:
#                         random_value = random.randint(0,max_type)
#                         if eval(expr, {'_': random_value}):
#                             return convert_value_to_type(random_value, field_type, endianness, encoding)
#                     except Exception as e:
#                         pass  # Ignore exceptions and retry
#                 raise ValueError("Unable to find a valid value satisfying the expression within the given range.")
#             elif isinstance(expr, dict):
#                 # Handle dictionary expressions if needed
#                 pass
#     elif valid_value is not None:
#         return convert_value_to_type(valid_value, field_type, endianness, encoding)
##MODIFIED this generate random string function
# def generate_random_string(size, encoding):
#     # Generate random string of given size
#     # For simplicity, let's assume ASCII characters for now
#     random_string = ''.join(random.choice(string.ascii_letters) for _ in range(size))
#     print("The random string is", random_string)
#     return random_string

def generate_random_string(size, encoding):
    if encoding.lower() in ['ascii', 'iso8859-1']:
        # Basic Latin character range: safe for both ASCII and ISO8859-1
        charset = [chr(i) for i in range(32, 127)]
    elif encoding.lower() in ['utf-8', 'utf8']:
        # UTF-8 supports wider Unicode — keep it in a moderate range
        charset = [chr(i) for i in range(32, 0x07FF)]
    elif encoding.lower() in ['utf-16le', 'utf-16']:
        # UTF-16 supports a large range — stay in BMP for safety
        charset = [chr(i) for i in range(32, 0xD7FF)]
    else:
        # Default to safe ASCII if encoding is unknown
        charset = list(string.ascii_letters)

    random_string = ''.join(random.choice(charset) for _ in range(size))
   #print("The random string is", random_string)
    return random_string



def handle_repeat_field(field, endian, parent,root,  parent_string):
    total_expansion = b''
    expansion = handle_field(field, endian, parent,root,parent_string)
    total_expansion += expansion
    append_value_to_node(field, expansion)
    random_repeat_count = random.randrange(1, 10)
    for _ in range(1, random_repeat_count):
        expansion = handle_field(field, endian, parent, root,parent_string)
        total_expansion += expansion
        append_value_to_node(field, expansion)
    
    return total_expansion


def handle_repeat_expr_field(field, endian, seq, parent,root, parent_string):
    endianness= '<' if endian == 'le' else '>'
    total_expansion=b''
    repeat_expr = field.get('repeat-expr')
    expansion = handle_field(field, endian, parent,root, parent_string)  #so that it occurs atleast 1 time
    total_expansion += expansion
    append_value_to_node(field, expansion)
    if repeat_expr is not None:
        if isinstance(repeat_expr, int):
            result = repeat_expr
        else:
            #result = evaluate_condition(repeat_expr, seq, endian, field)
            result= evaluate_condition(repeat_expr,root,parent,endianness, parent_string,  field)
    for _ in range(1,result):
        expansion = handle_field(field, endian, parent, root,parent_string)
        total_expansion += expansion
        append_value_to_node(field, expansion)
    
    return total_expansion
def handle_repeat_until_field(field, endian, seq, parent, root, parent_string):
    endianness= '<' if endian == 'le' else '>'
    size = evaluate_size(field.get('size', 0),root, endianness, parent, field)
    encoding = field.get('encoding')
    total_expansion=b''
    repeat_expr = field.get('repeat-until')
    max= random.randint(1, 100)
    #Handle _io.eof : Don't know if handling this here will solve every cases. 
    if repeat_expr=="_io.eof":
        while(max>0):
            expansion = handle_field(field, endian, parent,root, parent_string)
            total_expansion += expansion
            append_value_to_node(field, expansion)
            max=max-1
        return total_expansion
        
    while(max>0):
        expansion = handle_field(field, endian, parent,root, parent_string)
        
        result= evaluate_condition(repeat_expr,root,parent, endianness,parent_string,field)
        total_expansion += expansion
        append_value_to_node(field, expansion)
        if(result==True):
            break
        max=max-1
    if result==False:
        match = re.search(r'==\s*(\d+)', repeat_expr)
        if match:
            val = match.group(1)
            #print("The val in handle_repeat_until is ", val)
            rhs_val= convert_value_to_type(val,endianness,encoding, size)
            #print("The rhs_val in handle_repeat_until is ", rhs_val)
            total_expansion+=rhs_val
            append_value_to_node(field, rhs_val)
    return total_expansion




def handle_seq(seq, endian, parent,root, parent_string):
    total_expansion = b''
    endianness= '<' if endian == 'le' else '>'
    ####CHANGED ON 21-05-2025 due to problem in dependency in zip.ksy extra_field type fields: Dependency graph:  {'body': {'len_body'}, 'code': set(), 'len_body': set()} changed te function preprocess_kaitai_struct to add the switch case too.
    dependency_graph = preprocess_kaitai_struct(seq)
    ordered_list = dependency_order(dependency_graph)
    
   # print("Parent string in handle_seq", parent_string)
    for field_id in ordered_list:
       # print("Reached in handle_seq")
        field = next((item for item in seq if item['id'] == field_id), None)
       # print("Field in handle seq: ", field)
        if field is None:
            raise ValueError(f"Field ID '{field_id}' not found in the sequence.")
        condition_string= field.get('if')
        if condition_string is not None:
            #print("Seq is: ", seq)
            result = evaluate_condition(condition_string,root,parent,endianness,parent_string, field)
            #print("Result is: ",result)
            if(result==False):
                continue
        
        if field.get('repeat') is None:
            
            expansion = handle_field(field, endian, parent,root, parent_string)
        else:
            if field.get('repeat') == 'eos':
                expansion = handle_repeat_field(field, endian, parent, root,parent_string)
            elif field.get('repeat') == 'expr':
                expansion= handle_repeat_expr_field(field, endian, seq, parent, root, parent_string)
            elif field.get('repeat') == 'until':
                expansion= handle_repeat_until_field(field, endian, seq, parent, root, parent_string)
        
        #total_expansion += expansion
        
        add_value_to_node(field, expansion)
    total_expansion= calculate_total_expansion_in_current_seq(parent)
    return total_expansion

def handle_type(field,field_type,parent,endian, root, parent_string):
    endianness= '<' if endian == 'le' else '>'
    
    #field_type = field.get('type')
    size = evaluate_size(field.get('size', 0), root,endianness, parent, field )
    encoding = field.get('encoding')
    
    if field_type in ['u1', 'u2', 'u4', 'u8', 's2', 's4', 's8', 'f2', 'f4', 'f8',
                  'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8']:
        expansion = random_based_on_type(size, field_type, '<' if endian == 'le' else '>', encoding)
    elif field_type == 'str':
                if  (field.get('size-eos', False)==True):
                    size=random.randint(1,1024)
                    expansion = random_based_on_type(size, field_type, '<' if endian == 'le' else '>', encoding)
                else:
                    expansion = random_based_on_type(size, field_type, '<' if endian == 'le' else '>', encoding)
    elif  isinstance(field_type,dict) and 'switch-on'in field_type:
        switch_id=field_type['switch-on']
        cases=field_type['cases']
        expansion=handle_switch(field,root, parent,endian,parent_string,switch_id,cases)     
    elif field_type == 'strz':
        if 'size' in field:
            size = field['size']  
        else:
            size = random.randint(1, 1023)  

        if size < 1:
            size = 1
        random_string = generate_random_string(size, encoding)
        expansion = random_string.encode(encoding) + b'\0'

        
    else:
        print("USER DEFINED TYPE IS  ",field_type )
     #   print("FIELD IS ", field)
        expansion = handle_user_defined_type(field, parent, endian, field_type,root, parent_string)
    return expansion

def handle_user_defined_type(field, parent, endian, user_defined_type,data_tree, parent_string):
                

    
    #if parent is None:
    #    raise ValueError(" parent cannot be None.")
    
    expansion = b''
    #types_to_search = []
    
    # if parent is not None and 'types' in parent:
    #     types_to_search.append(parent['types'])
    # if grandparent is not None and 'types' in grandparent:
    #     types_to_search.append(grandparent['types'])
    #print('Parent_string in handle_type', parent_string)
  #  print("Userdefined type required, initial parent string ", user_defined_type, parent_string)
    types_dict, new_parent_string = find_user_defined_type(user_defined_type, parent_string, data_tree)
    #new_parent_string += "['types']"
    #new_parent_string += f"['{user_defined_type}']"
    #print("New_parent_string in handle_type:", new_parent_string)
    #print("Type dict in handle_type",types_dict)

    #for types_dict in types_to_search:
    #print("User-defined type is ", user_defined_type,"Type dict: ",  types_dict)
    #if user_defined_type in types_dict:
    type_entry = types_dict[user_defined_type]
    print("Type entry in handle_type",type_entry)
    #print("HERE:", type_entry.get('expansion'))
    #print("PARENT: ",parent)
    #expansion = handle_seq(type_entry['seq'], endian, type_entry, parent)
    #add_value_to_node(type_entry, expansion)
    # from here
    #if type_entry.get('expansion') is None:
   # print("HEREEEE:  ", type_entry)
    expansion=handle_seq(type_entry['seq'], endian, type_entry,data_tree, new_parent_string)
    add_value_to_node(type_entry,expansion )

    #To assign the value to length field if any
    #size_calc_flag = 0
    size_name = field.get('size', 0)
    size_val= len(expansion)
    if isinstance(size_name, str) and size_name!=None:
        #size_calc_flag = 1
        curr_dict= find_dict(parent_string, data_tree)
        endianness= '<' if endian == 'le' else '>'
        for item in curr_dict['seq']:
            if (item.get('id')==size_name):
                if(item.get('encoding') is not None and item.get('size') is not None):
                    item['expansion']=convert_value_to_type(size_val,item['type'],endianness, item['encoding'], item['size'])
                else:
                    item['expansion']=convert_value_to_type(size_val,item['type'],endianness, None , None)
                break
    #else:
    #    expansion= type_entry.get('expansion')
    #till here
    #break
    return expansion

# def find_user_defined_type(parent, user_defined_type):
#     if user_defined_type in parent['types']:
#         return parent['types'][user_defined_type]
#     elif 'parent' in parent:
#         return find_user_defined_type(parent['parent'], user_defined_type)
#     else:
#         return find_user_defined_type()


def calculate_total_expansion_in_current_seq(parent):
    total_expansion_in_current_seq=b''
    # Write the contents of 'expansion' field for each item in 'seq' to the file
    for item in parent['seq']:
        # repeat= item.get('repeat')
        field_value = item.get('expansion')
        if field_value is not None:
            total_expansion_in_current_seq+=field_value
    return total_expansion_in_current_seq

    # #Check if the 'if else' case is needed. 
    # else:
    #     curr_dict= find_dict(parent_string, data_tree)
    #     for item in curr_dict['seq']:
    #         if (item.get('id')==switch_id):
    #             print(f"Switching ID: {switch_id}, Value: {switch_val}, Type: {item['type']}") 
    #             if(item.get('encoding') is not None and item.get('size') is not None):
    #                 item['expansion']=convert_value_to_type(switch_val,item['type'],endianness, item['encoding'], item['size'])
    #             else:
    #                 item['expansion']=convert_value_to_type(switch_val,item['type'],endianness, None , None)
    #             break
            
           
def handle_switch(field,data_tree,parent,endian, parent_string,switch_id,case_dict):
        print("REACHED HANDLE SWITCH")
        tokens = switch_id.split('.')
        current_tree = data_tree if tokens[0] == '_root' else parent
        start_index = 1 if tokens[0] in ['_root', '_'] else 0
        endianness= '<' if endian == 'le' else '>'
        item= traverse_to_find_item(current_tree, tokens, start_index, data_tree, endianness)
        # if '::' in case_key:
        #     handle_case_key_enum_type()
        
        #clean_case_key = re.sub(r'^"|"$', '', str(case_key))
       
        # if '.' in switch_id:
        #     change_switch_id_for_dot_operator_path(switch_id, parent, data_tree, case_key, endianness)
        # else: 
        if item is not None:
          #  print("ITEM IS ", item)
            if is_enum_reference(case_dict, item):
                print("IT IS AN ENUM")
                case_value= find_case_key(data_tree,parent,item, case_dict, switch_id, endianness)
            else:
                print("IT IS NOT AN ENUM")
                case_key = random.choice(list(case_dict.keys()))
                case_value = case_dict[case_key]
            # change_switch_id(data_tree,parent, parent_string,case_key,switch_id, endianness)
                print("CASE KEY IS ", case_key)
                replace_value(item,case_key,endianness)
        else:
            print("ITEM IS NONE")
        
        print('IN HANDLE SWITCH case_value or type is ', case_value)
        expansion=handle_type(field,case_value,parent,endian,data_tree,parent_string)
        return expansion

def find_case_key(data_tree,parent,item, case_dict, switch_id, endianness):

    enum_val= item.get('expansion')
    print("ENUM VAL IS ", enum_val)
    enum_name= item.get('enum')
    field_type = item.get('type')
    if enum_name in data_tree['enums']:
        enums_list= data_tree['enums']
    elif enum_name in parent['enums']:
        enums_list= parent['enums']
    else:
        raise ValueError(f"Enumeration '{enum_name}' not found in the provided enums dictionary.")

    enum_values = enums_list[enum_name]
    # print("Enum_values is", enum_values)
    int_key = unpack_value_from_type(enum_val, field_type, endianness)

    try:
        result= enum_values[int_key]
    except KeyError:
        raise ValueError(f"Enum value {int_key} not found in enum '{enum_name}'")
    
    # result= enum_values[enum_val]
    
    for key in case_dict.keys():
        enum_tokens = key.split('::')
        if enum_tokens[1]==result:
            return case_dict[key]
        

#Changed this below function
# def change_switch_id(data_tree,parent,parent_string,switch_val,switch_id, endianness):
#     #if '.' in switch_id:
#         tokens = switch_id.split('.')
#         current_tree = data_tree if tokens[0] == '_root' else parent
#         start_index = 1 if tokens[0] in ['_root', '_'] else 0

#         item= traverse_to_find_item(current_tree, tokens, start_index, data_tree, endianness)
#         if item is not None:
#                 replace_value(item,switch_val,endianness)
#                 return True
#         return False



        # success = traverse_and_replace_value(current_tree, tokens, start_index, data_tree, switch_val, endianness)
        # if not success:
        #     print(f"Failed to set expansion for path {switch_id}")

# def handle_case_key_enum_type(case_key, data_tree, case )

# def change_switch_id_for_dot_operator_path(path_string, parent, data_tree, switch_val, endianness):
#     tokens = path_string.split('.')
#     current_tree = data_tree if tokens[0] == '_root' else parent
#     start_index = 1 if tokens[0] in ['_root', '_'] else 0

#     success = func2(current_tree, tokens, start_index, data_tree, switch_val, endianness)
#     if not success:
#         print(f"Failed to set expansion for path {path_string}")
def traverse_to_find_item(current_tree, tokens, index, data_tree, endianness):
    token = tokens[index]
    is_last = index == len(tokens) - 1
    if 'seq' not in current_tree:
        return None

    for item in current_tree['seq']:
        if item.get('id') == token:
            if is_last:
                # Found the target field
                # if(item.get('encoding') is not None and item.get('size') is not None):
                #     item['expansion']=convert_value_to_type(switch_val,item['type'],endianness, item['encoding'], item['size'])
                # else:
                #     item['expansion']=convert_value_to_type(switch_val,item['type'],endianness, None , None)
                return item
            field_type = item.get('type')
            if isinstance(field_type, str):
                # Follow the type reference
                type_def = data_tree.get('types', {}).get(field_type)
                if not type_def:
                    return None
                return traverse_to_find_item(type_def, tokens, index + 1, data_tree, endianness)
            else:
                return None
    return None
#def traverse_and_replace_value(current_tree, tokens, index, data_tree, switch_val, endianness):
    # item= traverse_to_find_item(current_tree, tokens, index, data_tree, endianness)
    # if item is not None:
    #         replace_value(item,switch_val,endianness)
    #         return True
    # return False

def replace_value(item, switch_val, endianness):

    if(item.get('encoding') is not None and item.get('size') is not None):
        item['expansion']=convert_value_to_type(switch_val,item['type'],endianness, item['encoding'], item['size'])
    else:
        item['expansion']=convert_value_to_type(switch_val,item['type'],endianness, None , None)


def is_enum_reference(case_dict, item):
    enum_name = item.get('enum')
    for key in case_dict:
        if isinstance(key, str) and key.startswith(f"{enum_name}::"):
            return True
    return False



