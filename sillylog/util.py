from os import (
    strerror,
    mkdir)
from os.path import (
    join as join_path,
    isdir,
    sep,
    realpath,
    dirname,
    expandvars,
    expanduser)


def flex_mkdir(directory_path, parents=True, shell_expand=True, is_filename=False):
    """Create a directory

    Parameters
    ----------

    If parents is True, create all parent directories as well
    If shell_expand is True, treat directory_path as a shell would
    If is_filename is True, treat directory_path as a filename
        Create only the parent directory for the file

    Returns
    -------
    Directory path
        Even if is_filename is True, return the directory path,
        not the file path

    Notes
    -----
    Equivalent to `mkdir -p <path>` in a shell

    Examples
    --------
    flex_mkdir('~/')    => mkdir -p /home/<user>/log
    flex_mkdir('$PWD') => mkdir -p <pwd>/log
    flex_mkdir('/tmp/log') => mkdir -p /tmp/log
    flex_mkdir('~/log/debug.log', is_filename=True) => mkdir -p /home/<user>/log

    Notes
    -----
    If directory is not a string, raise TypeError
    If failure due to permissions, raise OSError
    If failure due to other exception, raise exception
    """
    if not isinstance(directory_path, str):
        raise TypeError('Directory name must be a string value')
    path_stack = ''

    if shell_expand is True:
        directory_path = expandvars(expanduser(directory_path))

    # Normalize the path
    directory_path = realpath(directory_path)

    if is_filename is True:
        # Create the parent directory
        file_path = directory_path
        directory_path = dirname(directory_path)

    if isdir(directory_path):
        return directory_path if is_filename is not True else file_path

    try:
        for element in directory_path.split(sep):
            path_stack = join_path(sep, path_stack, element)
            if not isdir(path_stack):
                mkdir(path_stack)
        return file_path if is_filename is True else directory_path
    except OSError as err:
        print(strerror(err.errno))
        raise
    except Exception as err:
        print(repr(err))
        raise

