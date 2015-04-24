def clean_filename(filename, replace='', acceptable_chars=('.', '_')):
    """
    Take a file name and replace any non-alphanumeric characters (or any characters in acceptable_chars) with a
    replacement string (by default the empty string).
    :param filename: The filename to clean up.
    :param replace: (OPTIONAL) The character/string to replace all non-valid characters with. Default: empty string.
    :param acceptable_chars: (OPTIONAL) An iterable containing the acceptable characters to leave in the filename.
                             Default: ('.', '_')
    :return: A cleaned up filename.
    """
    return "".join([c if c.isalpha() or c.isdigit() or c in acceptable_chars else replace for c in filename])
