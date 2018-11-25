# jalWatcher

*THIS SCRIPT SUPPORTS JUST ONLY I NEEDED.*

JAL(Japan Airlines) is a transportation compony in Japan.

This script can browse(scrape) the JAL web reservation page and
find frights with reasonable price for specified route.

Scraping is implemented by [Selenium](https://docs.seleniumhq.org/) and [Firefox Headless mode](https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Headless_mode).

## Dependencies

Following modules must be installed.

- [Firefox](https://www.mozilla.org/ja/firefox/)
- [geckodriver](https://github.com/mozilla/geckodriver)
- [Selenium with Python](https://selenium-python.readthedocs.io/)

## Run

```shell
$ python3 src/start.py
```

You can optionally send logs to Slack channel.
Set environment variables as following to activate it.

```shell
export WATCHER_SLACK_WEBHOOK_URL="https://hooks.slack.com/services/Your/Webhook/URL"
export WATCHER_SLACK_USERNAME="YourUserName"
```
