# pyDownloader

<p align="center">
    <img src = "images/piratebay.png" height = 300px width = 300px>
</p>

> Downloading torrents from pirated sites is bit of a hassle. This Python based CLI helps you to download torrents with ease.

## Dependencies

- BeautifulSoup - `pip install bs4`
- Selenium - `pip install selenium`

## Requirements

Any of the following browsers:

- Chrome (Supports headless mode)
- Firefox
- Internet Explorer

> Note: Support for Firefox and IE browsers has not been implemented yet

## Usage

```
usage: pyratebay.py [-h] [-c [{all,audio,video,apps,games,other}]] query

positional arguments:
  query                 Name of the media to download

optional arguments:
  -h, --help            show this help message and exit
  -c, --category [{all,audio,video,apps,games,other}]
                        Searches for the given 'name' in the specified
                        category (default = all)
```

## From a developer standpoint

The newly updated pirate bay sites work differently. It fetches the data only after loading the webpage. The table is dynamically populated by JavaScript, this makes it impossible to scrape the data of the webpage using the normal `requests` or `urllib` module as it only returns a basic HTML content of the webpage without any table and other stuff. To overcome this problem, one should let the webpage load first and then scrape the contents of the webpage using the `selenium` or `bs4` modules. This way of scraping the web is known as dynamic web scraping, which is indeed implemented in this program.

<br>

![demo.gif](images/demo.gif)

<br>

## Credits

- [webdriver_manager](https://github.com/SergeyPirogov/webdriver_manager) - simplifies the management of binary drivers for different browsers

## License

[MIT](LICENSE) LICENSE
