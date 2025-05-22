import json
import uuid


def extract_text(response, extract_by="WORD"):
    line_text = []
    for block in response["Blocks"]:
        if block["BlockType"] == extract_by:
            line_text.append(block["Text"])
    return line_text


def map_word_id(response):
    word_map = {}
    for block in response["Blocks"]:
        if block["BlockType"] == "WORD":
            word_map[block["Id"]] = block["Text"]
        if block["BlockType"] == "SELECTION_ELEMENT":
            word_map[block["Id"]] = block["SelectionStatus"]
    return word_map


def extract_table_info(response, word_map):
    row = []
    table = {}
    ri = 0
    flag = False

    for block in response["Blocks"]:
        if block["BlockType"] == "TABLE":
            key = f"table_{uuid.uuid4().hex}"
            table_n = +1
            temp_table = []

        if block["BlockType"] == "CELL":
            if block["RowIndex"] != ri:
                flag = True
                row = []
                ri = block["RowIndex"]

            if "Relationships" in block:
                for relation in block["Relationships"]:
                    if relation["Type"] == "CHILD":
                        row.append(" ".join([word_map[i] for i in relation["Ids"]]))
            else:
                row.append(" ")

            if flag:
                temp_table.append(row)
                table[key] = temp_table
                flag = False
    return table


def get_key_map(response, word_map):
    key_map = {}
    for block in response["Blocks"]:
        if block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block["EntityTypes"]:
            for relation in block["Relationships"]:
                if relation["Type"] == "VALUE":
                    value_id = relation["Ids"]
                if relation["Type"] == "CHILD":
                    v = " ".join([word_map[i] for i in relation["Ids"]])
                    key_map[v] = value_id
    return key_map


def get_value_map(response, word_map):
    value_map = {}
    for block in response["Blocks"]:
        if block["BlockType"] == "KEY_VALUE_SET" and "VALUE" in block["EntityTypes"]:
            if "Relationships" in block:
                for relation in block["Relationships"]:
                    if relation["Type"] == "CHILD":
                        v = " ".join([word_map[i] for i in relation["Ids"]])
                        value_map[block["Id"]] = v
            else:
                value_map[block["Id"]] = "VALUE_NOT_FOUND"

    return value_map


def get_kv_map(key_map, value_map):
    final_map = {}
    for i, j in key_map.items():
        final_map[i] = "".join(["".join(value_map[k]) for k in j])
    return final_map


def parse_layout_blocks(response):
    # Create a block map for quick lookup
    block_map = {block["Id"]: block for block in response["Blocks"]}

    layout_items = []

    for block in response["Blocks"]:
        if "LAYOUT" in block["BlockType"]:
            layout_type = block.get("LayoutType", "UNKNOWN")
            text = ""

            # Get text from child relationships
            if "Relationships" in block:
                for relationship in block["Relationships"]:
                    if relationship["Type"] == "CHILD":
                        for child_id in relationship["Ids"]:
                            child_block = block_map[child_id]
                            if child_block["BlockType"] == "WORD":
                                text += child_block["Text"] + " "
                            elif child_block["BlockType"] == "LINE":
                                text += child_block["Text"] + "\n"

            layout_items.append(
                {
                    "type": layout_type,
                    "text": text.strip(),
                    "confidence": block["Confidence"],
                    "geometry": block["Geometry"],
                }
            )

    return layout_items


# with open("layout_check_data.json", "r") as file:
#     response = json.load(file)

# raw_text = extract_text(response, extract_by="LINE")
# word_map = map_word_id(response)
# table = extract_table_info(response, word_map)
# key_map = get_key_map(response, word_map)
# value_map = get_value_map(response, word_map)
# final_map = get_kv_map(key_map, value_map)
