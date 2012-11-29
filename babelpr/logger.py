import logging

class Logger(object):

    @classmethod
    def debug(cls, module, message):
        module_name = module.__class__.__name__.ljust(20)
        logging.debug("%s: %s" % (module_name, message))

    @classmethod
    def info(cls, module, message):
        module_name = module.__class__.__name__.ljust(20)
        logging.debug("%s: %s" % (module_name, message))

    @classmethod
    def warning(cls, module, message):
        module_name = module.__class__.__name__.ljust(20)
        logging.warn("%s: %s" % (module_name, message))

    @classmethod
    def error(cls, module, message):
        module_name = module.__class__.__name__.ljust(20)
        logging.debug("%s: %s" % (module_name, message))
