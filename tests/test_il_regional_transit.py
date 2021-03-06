# -*- coding: utf-8 -*-
from datetime import date, time

import pytest
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.constants import ADVISORY_COMMITTEE, BOARD, COMMITTEE
from city_scrapers.spiders.il_regional_transit import IlRegionalTransitSpider

freezer = freeze_time('2018-07-01')
freezer.start()
events_response = file_response(
    'files/il_regional_transit_calendar.html',
    url='http://www.rtachicago.org/about-us/board-meetings'
)
events_response.meta['event_description'] = (
    "The RTA Board of Directors typically meets each month on a Thursday at "
    "175 W. Jackson Blvd, Suite 1650 in Chicago. Board committee meetings "
    "typically begin at 8:30 a.m. Agendas are posted at least 48 hours prior "
    "to the meetings. All RTA Board meetings are audio taped. Recording of meetings "
    "starting December 2014 are available on the "
)

spider = IlRegionalTransitSpider()
parsed_items = [item for item in spider.parse_iframe(events_response) if isinstance(item, dict)]
freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Board of Directors'


def test_description():
    assert parsed_items[0]['event_description'] == (
        "The RTA Board of Directors typically meets each month on a Thursday at "
        "175 W. Jackson Blvd, Suite 1650 in Chicago. Board committee meetings "
        "typically begin at 8:30 a.m. Agendas are posted at least 48 hours prior "
        "to the meetings. All RTA Board meetings are audio taped. Recording of meetings "
        "starting December 2014 are available on the "
    )


def test_start():
    assert parsed_items[0]['start'] == {'date': date(2018, 6, 21), 'time': time(8, 30), 'note': ''}


def test_end_time():
    assert parsed_items[0]['end'] == {
        'date': None,
        'time': None,
        'note': '',
    }


def test_id():
    assert parsed_items[0]['id'] == 'il_regional_transit/201806210830/x/board_of_directors'


def test_status():
    assert parsed_items[0]['status'] == 'passed'
    assert parsed_items[-1]['status'] == 'tentative'


def test_documents():
    assert parsed_items[0]['documents'] == []
    assert parsed_items[1]['documents'] == [{
        'url': 'http://rtachicago.granicus.com/AgendaViewer.php?view_id=5&event_id=325',
        'note': 'agenda'
    }]


def test_classification():
    assert parsed_items[0]['classification'] == BOARD
    assert parsed_items[1]['classification'] == COMMITTEE


def test_parse_classification():
    assert spider._parse_classification('Board of Directors') == BOARD
    assert spider._parse_classification('Audit Committee') == COMMITTEE
    assert spider._parse_classification('Citizens Advisory Committee') == ADVISORY_COMMITTEE
    assert spider._parse_classification('Citizens Advisory Council') == ADVISORY_COMMITTEE
    assert spider._parse_classification('Citizens Advisory Board') == ADVISORY_COMMITTEE


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'name': 'RTA Administrative Offices',
        'address': '175 W. Jackson Blvd, Suite 1650, Chicago, IL 60604',
    }


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{
        'url': 'http://www.rtachicago.org/about-us/board-meetings',
        'note': ''
    }]
