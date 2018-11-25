import os
import logging
from logging.handlers import RotatingFileHandler

from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
seleniumLogger.setLevel(logging.WARNING)

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
LOG_FILE = '../logs/watcher.log'
SLACK_WEBHOOK_URL = os.environ.get('WATCHER_SLACK_WEBHOOK_URL')
SLACK_USERNAME = os.environ.get('WATCHER_SLACK_USERNAME')


FORMATTER = logging.Formatter(LOG_FORMAT)

def getStreamHandler():
  streamHandler = logging.StreamHandler()
  return streamHandler

def getFileHandler(logfile):
  fileHandler = RotatingFileHandler(filename=logfile,
                                     maxBytes=1024 * 1024,
                                     backupCount=9)
  return fileHandler

def getSlackHandler():
  if SLACK_WEBHOOK_URL is None:
    return None
  
  from slack_log_handler import SlackLogHandler
  slack_handler = SlackLogHandler(SLACK_WEBHOOK_URL,
                                  username=SLACK_USERNAME)
  return slack_handler

def getLogger(cwd):
  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)
  
  streamHandler = getStreamHandler()
  streamHandler.setLevel(logging.DEBUG)
  streamHandler.setFormatter(FORMATTER)
  logger.addHandler(streamHandler)

  logfile = os.path.join(cwd, LOG_FILE)
  logdir, _ = os.path.split(logfile)
  if not os.path.isdir(logdir):
    os.makedirs(logdir)
  fileHandler = getFileHandler(logfile)
  fileHandler.setLevel(logging.DEBUG)
  fileHandler.setFormatter(FORMATTER)
  logger.addHandler(fileHandler)
  
  slackHandler = getSlackHandler()
  if slackHandler is not None:
    slackHandler.setLevel(logging.WARN)
    slackHandler.setFormatter(FORMATTER)
    logger.addHandler(slackHandler)

  return logger
