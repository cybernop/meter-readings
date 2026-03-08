def confirm(string: str, default: bool = False) -> bool:

    if default:
        input_res = input(string + " [Yn]:")

        if input_res.lower() == "n":
            return False

        elif input_res.lower() == "y" or input_res == "":
            return True

    else:
        input_res = input(string + " [yN]:")

        if input_res.lower() == "n" or input_res == "":
            return False

        elif input_res.lower() == "y":
            return True

    return confirm(string)
