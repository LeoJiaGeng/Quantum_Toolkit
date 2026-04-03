__all__ = ["check_or_none", "check_list_all_int", "check_list_all_digit", "check_list_all_zero"]


def check_or_none(*args):
    """Check if the given arguments are not None"""
    if "" in args:
        return True
    return False


def check_list_all_int(check_list):
    for num in check_list:
        if not isinstance(num, int):
            return False
        return True


def check_list_all_digit(check_list):
    if len(check_list) == 1:
        return False
    for num in check_list:
        if not ((str(num).isdigit()) or (num[0] == '-' and num[1:].isdigit())):
            return False
        return True


def check_list_all_zero(check_list):
    for num in check_list:
        if str(int(num)) != "0":
            return False
        return True


if __name__ == "__main__":
    a = [1, 2, 3]
    print(check_list_all_digit(a))
    a = [0.0, "0", 0.00]
    print(check_list_all_zero(a))
