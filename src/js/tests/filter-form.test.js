const FilterForm = require('../organisms/filter-form');

// I wish there was a nicer way to get real HTML in here, rather than load a static copy-paste
const {
  PostsFilterFormTestHTML,
  PostsFilterFormTestHTMLWithSummaryData,
} = require('./filter-form-mock-html');

describe('test FilterForm bootstrapping behaviour', () => {
  const { location } = window;

  beforeAll(() => {
    delete window.location;
    window.location = {
      href: '',
      search: '',
    };
  });

  afterAll(() => {
    window.location = location;
  });

  beforeEach(() => {
    document.body.innerHTML = PostsFilterFormTestHTML;
  });

  test('test state population with no querystring params', () => {
    window.location.search = '';
    window.location.href = `https://example.com/${window.location.search}`;
    FilterForm.init();

    expect(
      document.querySelectorAll('input[type=checkbox]:checked'),
    ).toHaveLength(0);
    // clear triggers should all be hidden
    const clearSectionTriggers = document.querySelectorAll('a.js-filter-clear');
    const clearAllTriggerWrappers = document.querySelectorAll(
      'header.js-filter-form-clear-section',
    );
    expect(clearSectionTriggers).toHaveLength(3 * 2); // 3 * 2 because the form is duplicated in the HTML (mobile and desktop)
    expect(clearAllTriggerWrappers).toHaveLength(2);

    const hiddenClearSectionTriggers = Array.from(clearSectionTriggers).filter(
      (el) => el.hidden,
    );
    expect(hiddenClearSectionTriggers).toHaveLength(2 * 2); // one trigger for each of two sections, duplicated across two forms
    // The two triggers for clear-all are not hidden directly, but are hidden because their parent nodes are hidden:

    const clearTopicsTrigger = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'topic',
    )[0];
    const clearSearchTrigger = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'search',
    )[0];
    expect(clearTopicsTrigger.hidden).toBe(true);
    expect(clearSearchTrigger.hidden).toBe(true);

    const hiddenClearAllTriggerWrappers = Array.from(
      clearAllTriggerWrappers,
    ).filter((el) => el.hidden);
    expect(hiddenClearAllTriggerWrappers).toHaveLength(1 * 2); // one clear-all trigger per two forms

    // test content of search field too
    Array.from(document.querySelectorAll('.js-search-input')).forEach((el) => {
      expect(el.value).toBe('');
    });
  });

  test('test state with single topic', () => {
    window.location.search = '?topic=css';
    window.location.href = `https://example.com/${window.location.search}`;
    FilterForm.init();

    expect(
      document.querySelectorAll('input[type=checkbox]:checked'),
    ).toHaveLength(1 * 2); // duplicated forms, remember...

    const clearSectionTriggers = document.querySelectorAll('a.js-filter-clear');
    const clearAllTriggerWrappers = document.querySelectorAll(
      'header.js-filter-form-clear-section',
    );

    const hiddenClearSectionTriggers = Array.from(clearSectionTriggers).filter(
      (el) => el.hidden,
    );
    expect(hiddenClearSectionTriggers).toHaveLength(1 * 2); // one trigger for the Search section, duplicated across two forms

    const clearTopicsTrigger = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'topic',
    )[0];
    const clearSearchTrigger = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'search',
    )[0];
    expect(clearTopicsTrigger.hidden).toBe(false);
    expect(clearSearchTrigger.hidden).toBe(true);

    const hiddenClearAllTriggerWrappers = Array.from(
      clearAllTriggerWrappers,
    ).filter((el) => el.hidden);
    expect(hiddenClearAllTriggerWrappers).toHaveLength(0); // clear-all trigger is shown in mobile and desktop forms
    expect(clearAllTriggerWrappers).toHaveLength(2);

    // test content of search field too
    Array.from(document.querySelectorAll('.js-search-input')).forEach((el) => {
      expect(el.value).toBe('');
    });
  });

  test('test state with multiple topics', () => {
    window.location.search = '?topic=css&topic=javascript';
    window.location.href = `https://example.com/${window.location.search}`;
    FilterForm.init();

    expect(
      document.querySelectorAll('input[type=checkbox]:checked'),
    ).toHaveLength(2 * 2); // duplicated forms...

    expect(
      document.querySelectorAll("input[type=checkbox][value='css']:checked"),
    ).toHaveLength(1 * 2); // duplicated forms, remember...
    expect(
      document.querySelectorAll(
        "input[type=checkbox][value='javascript']:checked",
      ),
    ).toHaveLength(1 * 2); // duplicated forms, remember...

    const clearSectionTriggers = document.querySelectorAll('a.js-filter-clear');
    const clearAllTriggerWrappers = document.querySelectorAll(
      'header.js-filter-form-clear-section',
    );

    const hiddenClearSectionTriggers = Array.from(clearSectionTriggers).filter(
      (el) => el.hidden,
    );
    expect(hiddenClearSectionTriggers).toHaveLength(1 * 2); // one trigger for the Search section, duplicated across two forms

    const clearTopicsTrigger = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'topic',
    )[0];
    const clearSearchTrigger = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'search',
    )[0];
    expect(clearTopicsTrigger.hidden).toBe(false);
    expect(clearSearchTrigger.hidden).toBe(true);

    const hiddenClearAllTriggerWrappers = Array.from(
      clearAllTriggerWrappers,
    ).filter((el) => el.hidden);
    expect(hiddenClearAllTriggerWrappers).toHaveLength(0); // clear-all trigger is shown in mobile and desktop forms
    expect(clearAllTriggerWrappers).toHaveLength(2);

    // test content of search field too
    Array.from(document.querySelectorAll('.js-search-input')).forEach((el) => {
      expect(el.value).toBe('');
    });
  });

  test('test state with single topic and search', () => {
    window.location.search = '?topic=css&search=test+test';
    window.location.href = `https://example.com/${window.location.search}`;
    FilterForm.init();

    expect(
      document.querySelectorAll('input[type=checkbox]:checked'),
    ).toHaveLength(1 * 2); // duplicated forms, remember...
    expect(
      document.querySelectorAll("input[type=checkbox][value='css']:checked"),
    ).toHaveLength(1 * 2); // duplicated forms, remember...

    const clearSectionTriggers = document.querySelectorAll('a.js-filter-clear');
    const clearAllTriggerWrappers = document.querySelectorAll(
      'header.js-filter-form-clear-section',
    );

    const hiddenClearSectionTriggers = Array.from(clearSectionTriggers).filter(
      (el) => el.hidden,
    );
    expect(hiddenClearSectionTriggers).toHaveLength(0);

    const clearTopicsTrigger = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'topic',
    )[0];
    const clearSearchTrigger = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'search',
    )[0];
    expect(clearTopicsTrigger.hidden).toBe(false);
    expect(clearSearchTrigger.hidden).toBe(false);

    const hiddenClearAllTriggerWrappers = Array.from(
      clearAllTriggerWrappers,
    ).filter((el) => el.hidden);
    expect(hiddenClearAllTriggerWrappers).toHaveLength(0); // clear-all trigger is shown in mobile and desktop forms
    expect(clearAllTriggerWrappers).toHaveLength(2);

    // test content of search field too
    Array.from(document.querySelectorAll('.js-search-input')).forEach((el) => {
      expect(el.value).toBe('test test');
    });
  });

  test('test state with multiple topics and search', () => {
    window.location.search = '?topic=css&topic=javascript&search=test+test';
    window.location.href = `https://example.com/${window.location.search}`;
    FilterForm.init();

    expect(
      document.querySelectorAll('input[type=checkbox]:checked'),
    ).toHaveLength(2 * 2); // duplicated forms, remember...

    expect(
      document.querySelectorAll("input[type=checkbox][value='css']:checked"),
    ).toHaveLength(1 * 2); // duplicated forms, remember...
    expect(
      document.querySelectorAll(
        "input[type=checkbox][value='javascript']:checked",
      ),
    ).toHaveLength(1 * 2); // duplicated forms, remember...

    const clearSectionTriggers = document.querySelectorAll('a.js-filter-clear');
    const clearAllTriggerWrappers = document.querySelectorAll(
      'header.js-filter-form-clear-section',
    );

    const hiddenClearSectionTriggers = Array.from(clearSectionTriggers).filter(
      (el) => el.hidden,
    );
    expect(hiddenClearSectionTriggers).toHaveLength(0);

    const clearTopicsTrigger = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'topic',
    )[0];
    const clearSearchTrigger = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'search',
    )[0];
    expect(clearTopicsTrigger.hidden).toBe(false);
    expect(clearSearchTrigger.hidden).toBe(false);

    const hiddenClearAllTriggerWrappers = Array.from(
      clearAllTriggerWrappers,
    ).filter((el) => el.hidden);
    expect(hiddenClearAllTriggerWrappers).toHaveLength(0); // clear-all trigger is shown in mobile and desktop forms
    expect(clearAllTriggerWrappers).toHaveLength(2);

    // test content of search field too
    Array.from(document.querySelectorAll('.js-search-input')).forEach((el) => {
      expect(el.value).toBe('test test');
    });
  });

  test('test state with only search', () => {
    window.location.search = '?search=test+test';
    window.location.href = `https://example.com/${window.location.search}`;
    FilterForm.init();

    expect(
      document.querySelectorAll('input[type=checkbox]:checked'),
    ).toHaveLength(0); // no topics selected

    const clearSectionTriggers = document.querySelectorAll('a.js-filter-clear');
    const clearAllTriggerWrappers = document.querySelectorAll(
      'header.js-filter-form-clear-section',
    );

    const hiddenClearSectionTriggers = Array.from(clearSectionTriggers).filter(
      (el) => el.hidden,
    );
    expect(hiddenClearSectionTriggers).toHaveLength(1 * 2); // one trigger for the Topics section, duplicated across two forms

    const clearTopicsTrigger = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'topic',
    )[0];
    const clearSearchTrigger = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'search',
    )[0];
    expect(clearTopicsTrigger.hidden).toBe(true);
    expect(clearSearchTrigger.hidden).toBe(false);

    const hiddenClearAllTriggerWrappers = Array.from(
      clearAllTriggerWrappers,
    ).filter((el) => el.hidden);
    expect(hiddenClearAllTriggerWrappers).toHaveLength(0); // clear-all trigger is shown in mobile and desktop forms
    expect(clearAllTriggerWrappers).toHaveLength(2);

    // test content of fields too
    Array.from(document.querySelectorAll('.js-search-input')).forEach((el) => {
      expect(el.value).toBe('test test');
    });
  });
});

describe('test FilterForm clearing fields', () => {
  const { location } = window;

  beforeAll(() => {
    delete window.location;
    window.location = {
      href: '',
      search: '',
    };
  });

  afterAll(() => {
    window.location = location;
  });

  beforeEach(() => {
    document.body.innerHTML = PostsFilterFormTestHTML;
  });

  test('test clearing all fields', () => {
    window.location.search = '?topic=css&topic=javascript&search=test+test';
    window.location.href = `https://example.com/${window.location.search}`;

    FilterForm.init();

    // confirm the forms is populated as expected
    expect(
      document.querySelectorAll("input[type=checkbox][value='css']:checked"),
    ).toHaveLength(1 * 2); // duplicated forms, remember...
    expect(
      document.querySelectorAll(
        "input[type=checkbox][value='javascript']:checked",
      ),
    ).toHaveLength(1 * 2); // duplicated forms, remember...

    Array.from(document.querySelectorAll('.js-search-input')).forEach((el) => {
      expect(el.value).toBe('test test');
    });

    const clearAllTriggers = document.querySelectorAll(
      '.js-filter-form-clear-section a.js-filter-clear',
    );
    expect(clearAllTriggers.length).toBe(2);

    // clear all fields
    Array.from(clearAllTriggers).forEach((el) => el.click());

    // confirm the forms are cleared as expected
    expect(
      document.querySelectorAll("input[type=checkbox][value='css']:checked"),
    ).toHaveLength(0); // duplicated forms, remember...
    expect(
      document.querySelectorAll(
        "input[type=checkbox][value='javascript']:checked",
      ),
    ).toHaveLength(0); // duplicated forms, remember...

    Array.from(document.querySelectorAll('.js-search-input')).forEach((el) => {
      expect(el.value).toBe('');
    });
  });

  test('test clearing sections', () => {
    window.location.search = '?topic=css&topic=javascript&search=test+test';
    window.location.href = `https://example.com/${window.location.search}`;

    FilterForm.init();

    // confirm the forms is populated as expected
    expect(
      document.querySelectorAll("input[type=checkbox][value='css']:checked"),
    ).toHaveLength(1 * 2); // duplicated forms, remember...
    expect(
      document.querySelectorAll(
        "input[type=checkbox][value='javascript']:checked",
      ),
    ).toHaveLength(1 * 2); // duplicated forms, remember...

    Array.from(document.querySelectorAll('.js-search-input')).forEach((el) => {
      expect(el.value).toBe('test test');
    });

    const clearAllTriggers = document.querySelectorAll(
      '.js-filter-form-clear-section a.js-filter-clear',
    );
    expect(clearAllTriggers.length).toBe(2);
    const clearSectionTriggers = document.querySelectorAll('a.js-filter-clear');
    expect(clearSectionTriggers.length).toBe(6);
    const clearTopicsTriggers = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'topic',
    );
    const clearSearchTriggers = Array.from(clearSectionTriggers).filter(
      (el) => el.getAttribute('data-controls') === 'search',
    );

    expect(clearTopicsTriggers.length).toBe(2);
    expect(clearSearchTriggers.length).toBe(2);

    // clear all topics
    Array.from(clearTopicsTriggers).forEach((el) => el.click());

    // confirm the forms are cleared as expected
    expect(
      document.querySelectorAll("input[type=checkbox][value='css']:checked"),
    ).toHaveLength(0); // duplicated forms, remember...
    expect(
      document.querySelectorAll(
        "input[type=checkbox][value='javascript']:checked",
      ),
    ).toHaveLength(0); // duplicated forms, remember...

    // search not cleared yet
    Array.from(document.querySelectorAll('.js-search-input')).forEach((el) => {
      expect(el.value).toBe('test test');
    });

    // clear search
    Array.from(clearSearchTriggers).forEach((el) => el.click());
    Array.from(document.querySelectorAll('.js-search-input')).forEach((el) => {
      expect(el.value).toBe('');
    });
  });
});

describe('test FilterForm clearing also clears mobile summary', () => {
  const { location } = window;

  beforeAll(() => {
    delete window.location;
    window.location = {
      href: '',
      search: '',
    };
  });

  afterAll(() => {
    window.location = location;
  });

  beforeEach(async () => {
    // include HTML that simulates there being content in the summary div
    document.body.innerHTML = PostsFilterFormTestHTMLWithSummaryData;

    expect(
      document.querySelectorAll('.js-filter-form-summary--search').length,
    ).toBe(1);
    expect(
      document.querySelectorAll('.js-filter-form-summary--search')[0].innerHTML,
    ).toBe("Searched for: 'test test'");

    expect(
      document.querySelectorAll('.js-filter-form-summary--filters').length,
    ).toBe(1);
    expect(
      document.querySelectorAll('.js-filter-form-summary--filters')[0]
        .innerHTML,
    ).toBe("Filters: 'test test'");
  });

  test('test clearing search fields empties the search summary shown for mobile', () => {
    window.location.search = '?topic=css&topic=javascript&search=test+test';
    window.location.href = `https://example.com/${window.location.search}`;

    FilterForm.init();

    document
      .querySelectorAll('.js-filter-clear[data-controls="search"]')[0]
      .click();

    expect(
      document.querySelectorAll('.js-filter-form-summary--search')[0].innerHTML,
    ).toBe('');

    expect(
      document.querySelectorAll('.js-filter-form-summary--filters')[0]
        .innerHTML,
    ).toBe("Filters: 'test test'");
  });

  test('test clearing any filter fields empties the filter summary shown for mobile', () => {
    FilterForm.init();
    document
      .querySelectorAll('.js-filter-clear[data-controls="topic"]')[0]
      .click();

    expect(
      document.querySelectorAll('.js-filter-form-summary--search')[0].innerHTML,
    ).toBe("Searched for: 'test test'");

    expect(
      document.querySelectorAll('.js-filter-form-summary--filters')[0]
        .innerHTML,
    ).toBe('');
  });

  test('test clearing all params empties the search summary AND filter summary', () => {
    FilterForm.init();
    document
      .querySelectorAll('.js-filter-form-clear-section a.js-filter-clear')[0]
      .click();

    expect(
      document.querySelectorAll('.js-filter-form-summary--search')[0].innerHTML,
    ).toBe('');

    expect(
      document.querySelectorAll('.js-filter-form-summary--filters')[0]
        .innerHTML,
    ).toBe('');
  });
});
