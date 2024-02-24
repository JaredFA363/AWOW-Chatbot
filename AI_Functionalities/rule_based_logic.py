
# negation function
def adjust_negation(expression):
    if expression[0] == '-':
        # Remove the leading "-"
        return expression[1:]
    else:
        # Add a leading "-"
        return '-' + expression

def extract_wonder_name(statement):
    """
    Extract wonder name and category from the statement between "Check that" and "is".
    Return the wonder name without spaces.
    """
    start_index = statement.find("Check that") + len("Check that")
    end_index = statement.find("is")

    if start_index == -1 or end_index == -1:
        return None, None  # "Check that" or "is" not found in the statement

    # Extract the wonder name and category
    wonder_info = statement[start_index:end_index].strip()
    wonder_info = wonder_info.replace(" ", "")  # Remove spaces
    wonder_name, category = wonder_info, statement[end_index+3:].strip()  # Extract category after "is"

    return wonder_name, category

def extract_wonder_name_kb_addition(statement):
    """
    Extract wonder name and category from the statement between "Check that" and "is".
    Return the wonder name without spaces.
    """
    start_index = statement.find("i know that") + len("i know that ")
    end_index = statement.find("is")

    if start_index == -1 or end_index == -1:
        return None, None  # "Check that" or "is" not found in the statement

    # Extract the wonder name and category
    wonder_info = statement[start_index:end_index].strip()
    wonder_info = wonder_info.replace(" ", "")  # Remove spaces
    wonder_name, category = wonder_info, statement[end_index+3:].strip()  # Extract category after "is"

    return wonder_name, category