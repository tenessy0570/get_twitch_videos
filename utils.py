def dict_to_str(my_dict: dict):
    formatted = "\n\n".join((f"{title}: \n" + my_dict[title] for title in my_dict))
    return formatted
