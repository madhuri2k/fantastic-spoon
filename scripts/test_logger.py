#import logging module
import logging
#Create a logger object
logger=logging.getLogger()
#Configure logger
logging.basicConfig ( filename="test.log", format='%(filename)s: %(message)s', filemode='w')
#Setting threshold level
logger.setLevel(logging.DEBUG)
#Use the logging methods
logger.debug("This is a debug message")
logger.info("For your info")
logger.warning('This is a warning message')
logger.error("This is an error message")
logger.critical("This is a critical message")
