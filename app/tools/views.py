import logging
from django.http import HttpResponse

logger = logging.getLogger(__name__)

def test_logging(request):
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    return HttpResponse("Logging test complete. Check your logs.")