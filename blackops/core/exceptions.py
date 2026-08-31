CONFIG_SHARE_NOT_FOUND = "Config share path doesn't exist: {}. Please ensure that you have placed the `config.share` file in the same directory as the current notebook, or otherwise you must specify the right location of the file in `config_share_path` argument."


class ConfigShareNotFound(ValueError):
    pass


class InvalidTableName(ValueError):
    pass
