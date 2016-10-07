# -*- coding: utf-8 -*-
import re
import bs4
import arrow
import requests

from HTMLParser import HTMLParseError
from chalice import Chalice


app = Chalice(app_name='top40-chalice')

# The return object is a plain dict, unlike Flask, which expects a response
@app.route('/')
def index():
    return {'hello': 'world'}

# The view function above will return {"hello": "world"}
# whenver you make an HTTP GET request to '/'.

# The following code is extracted from `pythontop40server`
# Copyright 2014 Danny Goodall
def strip_number_suffix(string):
    return re.sub(r'(\d)(st|nd|rd|th)', r'\1', string)


def get_change_dict(position, previous):
    """Return a dictionary that describes the change since last week using Ben Major's API format.

    One change from Ben Major's format is that new entries will show as an "up" change and the actual and amount
    parts will be computed as if the single or album was at #41 the previous week. Therefore an entry that is straight
    in at number 1, will show an amount and actual move of 40 places.

    >>> change_dict(11,16)
    >>> {"direction": "up", "amount": 5. "actual": 5}

    >>> change_dict(11,0)
    >>> {"direction": "up", "amount": 30. "actual": 30}

    >>> change_dict(16,11)
    >>> {"direction": "down", "amount": 0, "actual": -5}

    >>> change_dict(11,11)
    >>> {"direction": "none", "amount": 0, "actual": 0}

    Args:
        position (:py:class:`int`) : The position in the chart 1-40
        previous (:py:class:`int`) : Last week's chart position

    Returns:
        change_dict (:py:class:`dict`) : A dictionary containing keys that describe the Change since last week
    """
    actual = (previous if previous else 41) - position
    amount = abs(actual)
    if actual > 0:
        direction="up"
    elif actual < 0:
        direction="down"
    else:
        direction="none"

    return dict(direction=direction, actual=actual, amount=amount)


def get_page_date(page_title):
    """Return the date of the chart by extracting it from the title

    The page title is passed in this format

    >>> page_title = "The Official UK Top 40 Albums Chart - 30th November 2014"

    The strategy is to split the string on the -

    >>> page_title.split("-")[1]
    >>> " 30th November 2014")

    Trim the leading space

    >>> page_title.lstrip()
    >>> "30th November 2014"

    Then remove the number suffix (th,st,nd,rd)

    >>> date_string = strip_number_suffix(page_title)
    >>> "30 November 2014"

    And finally to to parse the string and convert to a date

    >>> date_of_chart = arrow.get(date_string,["D MMMM YYYY", "DD MMMM YYYY"])
    >>> <Arrow [2014-11-30T00:00:00+00:00]>

    Args:
        page_title (:py:class:`str`) : The title extracted from the HTML page

    Returns
        date_of_chart (:py:class:`Arrow`) : The date of the chart as an Arrow date.
    """
    if not page_title:
        raise Exception("No title was found in the html document")
    if not "-" in page_title:
        raise Exception("Page title incorrectly formed.")

    # Split the page title on the - and take the right hand side
    date_string = page_title.split("-")[1].lstrip()
    # Remove the number suffix st, nd, rd, th
    date_string = strip_number_suffix(date_string)
    # Create a date format
    try:
        date_of_chart = arrow.get(date_string, ["D MMMM YYYY", "DD MMMM YYYY"])
    except RuntimeError:
        raise Exception("Couldn't parse the title to get the chart date.")

    return date_of_chart


@app.route('/singles')
def scrape_bbc_page(chart_type="singles"):
    """Scrape the relevant page on the BBC website and return chart information

    Looks for the relevant page, downloads it and extracts the chart information from the HTML. Returns the chart
    information as a dictionary in the format define by `Ben Major here <http://ben-major.co.uk/2013/12/uk-top-40-charts-api/>`_.

    >>> #IF THE ATTEMPT TO READ THE BBC SITE FAILS
    >>> scrape_bbc_page()
    >>> {}

    >>> scrape_bbc_page("singles")
    >>> {
    >>>     "date": 1386460800,
    >>>     "retrieved": 1386669718,
    >>>     "entries":
    >>>     [
    >>>        {
    >>>            "position": 1,
    >>>            "previousPosition": 1,
    >>>            "numWeeks": 2,
    >>>            "artist": "One Direction",
    >>>            "title": "Midnight Memories",
    >>>            "change":
    >>>            {
    >>>                "direction": "none",
    >>>                "amount": 0,
    >>>                "actual": 0
    >>>            }
    >>>        },
    >>>        .
    >>>        .
    >>>        .
    >>>    ]
    >>> }

    Used some of the logic for scraping a table from this page: http://stackoverflow.com/a/18966444/1300916

    The page being scraped has the following structure

    <html lang="en-gb">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <meta name="robots" content="noindex">
            <link rel="stylesheet" href="http://static.bbci.co.uk/radio/663/1.33/style/components/chart_print.css">
            <link rel="stylesheet" href="http://static.bbci.co.uk/radio/663/1.33/style/components/masthead_logos.css">
            <title>The Official UK Top 40 Singles Chart - 7th December 2014</title>
        </head>
        <body class="service-bbc_radio_one">
            <div class="masterbrand-logo"></div>
            <h1>The Official UK Top 40 Singles Chart - 7th December 2014</h1>
            <table border="1" cellpadding="3" cellspacing="0">
                <tbody>
                    <tr>
                        <th>Position</th>
                        <th>Status</th>
                        <th>Previous</th>
                        <th>Weeks</th>
                        <th>Artist</th>
                        <th>Title</th>
                    </tr>
                        <tr>
                            <td>1</td>
                            <td>up 3</td>
                            <td>4</td>
                            <td>24</td>
                            <td>Ed Sheeran</td>
                            <td>Thinking Out Loud</td>
                        </tr>
                        <tr>
                            <td>2</td>
                            <td>new</td>
                            <td></td>
                            <td>1</td>
                            <td>Union J</td>
                            <td>You Got It All</td>
                        </tr>
                        <tr>
                            <td>3</td>
                            <td>down 2</td>
                            <td>1</td>
                            <td>2</td>
                            <td>Take That</td>
                            <td>These Days</td>
                        </tr>
                        .
                        .
                        .
                       <tr>
                            <td>40</td>
                            <td>down 4</td>
                            <td>36</td>
                            <td>2</td>
                            <td>Beyoncé</td>
                            <td>7/11</td>
                        </tr>
                </tbody>
            </table>
        </body>
    </html>

    Args:
        page_type (:py:class:`str`): Either "albums" or "singles" - defaults to albums. This defines the type of chart
            that is requested.

    Returns:
        chart_info (:py:class:`dict`): A dictionary that describes the chart information
    """

    # Create a page template for the BBC site. Insert either singles or albums based on chart_type
    page = "http://www.bbc.co.uk/radio1/chart/{}/print".format(chart_type)

    # Create a list of the columns that will be enountered and their corresponding names and types
    unpacking_list = [
        ("position", int),
        ("status", str),
        ("previousPosition", int),
        ("numWeeks", int),
        ("artist", str),
        ("title", str)
    ]

    # Initialise our containers
    chart_dict = {}
    entries = []

    # There are many errors that can occur whilst we're trying to get the stuff from the BBC site
    # Let's catch them and then re-raise them as our own Exception
    try:
        html_text = requests.get(page)
        html_text.encoding = 'utf-8'
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
        raise Exception("A connection error or connection timeout error occurred.")
    except requests.exceptions.HTTPError as e:
        raise Exception("An HTTP error was returned from the remote server")

    # We could get parse errors in the HTML, so let's raise an Exception if we do
    try:
        soup = bs4.BeautifulSoup(html_text.text, "html.parser")
    except (UnicodeEncodeError, KeyError, AttributeError, HTMLParseError) as e:
        raise Exception("Couldn't parse the text from "+page)

    # Now grab the date of the chart from the page title
    page_date = get_page_date(page_title=soup.find('title').string)
    todays_date = arrow.utcnow()

    # Find all table rows in the HTML document
    table_rows = soup.find_all("tr")
    if not table_rows:
        return chart_dict

    # Loop through the rows in the table - ignoring the header row
    for table_row in table_rows[1:]:
        entry_dict = {}
        table_data = table_row.find_all("td")

        # Now unpack the table_data and convert if necessary
        for column, column_info in enumerate(unpacking_list):
            # Set the dictionary key and conversion class to use
            dict_key, conversion_type = column_info

            # Set the column string or initialise an equivalent type if it is None
            column_string = table_data[column].string.encode('utf-8') if table_data[column].string else conversion_type()

            # Assign the value from the web table to our entry dictionary, converting it as we go
            entry_dict[dict_key] = conversion_type(column_string)

        # Compute the change dict, based on this entry
        change_dict = get_change_dict(entry_dict["position"], entry_dict["previousPosition"])

        # Store the change dict away in the "change" key of our entry dict
        entry_dict["change"] = change_dict

        # Add the entry dictionary to the chart entries list - but remove the status key first as this isn't part of the
        # Booby model.
        entries.append(entry_dict)

    # Finished processing the rows, so now fill the container with what we saw
    chart_dict["date"] = page_date.timestamp
    chart_dict["retrieved"] = todays_date.timestamp
    chart_dict["entries"] = entries

    return chart_dict
