import os
import time
from selenium import webdriver
from logger import getLogger

def getBrowser(logdir='geckodriver.log', headless=True):
  options = webdriver.FirefoxOptions()
  if headless:
    options.add_argument('-headless')
  browser = webdriver.Firefox(options=options, log_path=logdir)
  return browser

class BrowsingException(RuntimeError):
  pass

def getNth(es, i=0):
  if len(es) > i:
    return es[i]
  else:
    raise BrowsingException('getNth')

class JALBrowser(object):
  def __init__(self, browser, logger=None):
    self.browser = browser
    if logger is None:
      logger = logging.getLogger()
    self.logger = logger

  def gotoTop(self):
    self.browser.get('https://www.jal.co.jp/')
  
  def skipAdvertise(self):
    try:
      skipButton = self.browser.find_element_by_id('JS_skip')
      self.logger.debug('Skipping advertise...')
      skipButton.click()
    except Exception as e:
      print(e)
  
  def processCalendar(self, month, mday):
    browser = self.browser
    monthes = browser.find_elements_by_css_selector('#JS_calendar h3')
    for _ in range(0, 5):
      for i in range(0, len(monthes)):
        monthTexts = monthes[i].find_elements_by_tag_name('span')
        self.logger.debug('monthTexts[{i}/{a}]={t}'
                          .format(i=i, a=len(monthTexts), t=monthTexts[0].text))
        if str(month) == getNth(monthTexts, 0).text:
          className = 'calendar-wrap-{i}'.format(i=i+1)
          self.logger.debug('Looking for class, {n}'.format(n=className))
          monthWrap = getNth(browser.find_elements_by_class_name(className), 0)
          monthWrap.find_element_by_link_text(str(mday)).click()
          return
      self.logger.debug('Turning over calendar...')
      time.sleep(1)
      getNth(browser.find_elements_by_class_name('calendar-next a'), 0).click()
      monthes = browser.find_elements_by_css_selector('#JS_calendar h3')
    raise BrowsingException('processCalendar')

  def searchPriceTable(self, departure, arrival, month, mday):
    browser = self.browser
    self.logger.debug('Configuring form...')
    browser.find_element_by_id('JS_oneWay').click()
    browser.find_element_by_id('JS_domDepAir').click()
    browser.find_element_by_link_text(departure).click()
    browser.find_element_by_id('JS_domArrAir').click()
    browser.find_element_by_link_text(arrival).click()
    browser.find_element_by_id('JS_domLbDepDate').click()
    self.logger.debug('Selecting departure date...')
    self.processCalendar(month, mday)
    time.sleep(1)
    self.logger.debug('Searching submitted.')
    submitButton = browser.find_element_by_id('JS_submitBtn').click()
    time.sleep(5)
    self.logger.debug('Current page is {t}.'.format(t=browser.title))
    if '空席照会結果' not in self.browser.title:
      raise BrowsingException('Not navigated')
    self.logger.debug('Searching done.')

  def getPrices(self, es):
    prices = []
    for e in es:
      if 'links' not in e.get_attribute('class'):
        continue
      spans = e.find_elements_by_tag_name('span')
      if len(spans) > 0:
        price = spans[0].text.replace(',', '')
        prices.append(int(price))
    return prices

  def readPriceTable(self):
    browser = self.browser
    self.logger.debug('Reading fright table...')
    priceTable = []
    farelistTable = browser.find_element_by_id('farelistTableA01')
    farelist = farelistTable.find_elements_by_tag_name('tr')
    for i in range(0, len(farelist)):
      fareitem = farelist[i]
      frights = fareitem.find_elements_by_class_name('flight')
      if len(frights) == 0: continue
      fright = frights[0].text
      self.logger.debug('Fetching {f}...'.format(f=fright))
      departure = getNth(fareitem.find_elements_by_css_selector('.departure'), 0)
      departureTime, departureAirport = departure.text.split('\n')
      arrival = getNth(fareitem.find_elements_by_css_selector('.arrival'), 0)
      arrivalTime, arrivalAirport = arrival.text.split('\n')
      prices0 = self.getPrices(fareitem.find_elements_by_css_selector('.jsPrice'))
      prices1 = self.getPrices(farelist[i+1].find_elements_by_css_selector('.jsPrice'))
      prices = prices0 + prices1
      priceTable.append({'fright': fright,
                         'departureTime': departureTime,
                         'departureAirport': departureAirport,
                         'arrivalTime': arrivalTime,
                         'arrivalAirport': arrivalAirport,
                         'prices': prices})
    return priceTable

  def browsePriceTableOf(self, departure, arrival, month, mday):
    self.gotoTop()
    self.skipAdvertise()
    self.searchPriceTable(departure, arrival, month, mday)
    return self.readPriceTable()

  def close(self):
    self.browser.close()
  
def isTargetFlight(i):
  return (i['arrivalTime'] < '11:00' and \
          len(i['prices']) > 0 and \
          min(i['prices']) < 20000)

def main():
  cwd = os.path.dirname(os.path.abspath(__file__))
  logger = getLogger(cwd)
  logger.debug('Initializing browser...')
  browser = JALBrowser(getBrowser(logdir='logs/geckodriver.log', headless=True),
                       logger=logger)
  logger.debug('Start browsing...')
  priceTable = browser.browsePriceTableOf('東京(羽田)', '札幌(新千歳)', 2, 9)
  targetFrights = list(filter(isTargetFlight, priceTable))
  if len(targetFrights) > 0:
    logger.warn('Nice frights detected!, {f}'.format(f=targetFrights))
  else:
    logger.info('No nice frights detected.')
  browser.close()
    

if __name__ == '__main__':
  main()
