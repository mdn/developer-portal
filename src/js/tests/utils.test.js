const { decodeFormURLEncodedSpaces, parseQueryParams } = require('../utils');

describe('test decodeFormURLEncodedSpaces', () => {
  test('Happy path', () => {
    expect(decodeFormURLEncodedSpaces('foo+bar')).toBe('foo bar');
  });
  test('No + means no change', () => {
    expect(decodeFormURLEncodedSpaces('foo bar')).toBe('foo bar');
  });
  test('Percent-encoded space ignored by this helper', () => {
    expect(decodeFormURLEncodedSpaces('foo%20bar')).toBe('foo%20bar');
  });
  test('Percent-encoded + ignored by this helper', () => {
    expect(decodeFormURLEncodedSpaces('foo%2Bbar')).toBe('foo%2Bbar');
  });
});

describe('test parseQueryParams', () => {
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

  test('no params', () => {
    window.location.search = '';
    window.location.href = `https://example.com/${window.location.search}`;
    expect(parseQueryParams()).toMatchObject({});

    window.location.search = '?';
    window.location.href = `https://example.com/${window.location.search}`;
    expect(parseQueryParams()).toMatchObject({});
  });

  test('single topic', () => {
    window.location.search = '?topic=foo';
    window.location.href = `https://example.com/${window.location.search}`;
    expect(parseQueryParams()).toMatchObject({ topic: ['foo'] });
  });

  test('single topic and search', () => {
    window.location.search = '?topic=foo&search=hello+world';
    window.location.href = `https://example.com/${window.location.search}`;
    expect(parseQueryParams()).toMatchObject({
      topic: ['foo'],
      search: ['hello+world'],
    });
  });
  test('single topic and search, swapped order makes no difference', () => {
    window.location.search = '?search=hello+world&topic=foo';
    window.location.href = `https://example.com/${window.location.search}`;
    expect(parseQueryParams()).toMatchObject({
      topic: ['foo'],
      search: ['hello+world'],
    });
  });

  test('mutiple topic and search', () => {
    window.location.search = '?topic=foo&topic=bar&search=hello+world';
    window.location.href = `https://example.com/${window.location.search}`;
    expect(parseQueryParams()).toMatchObject({
      topic: ['foo', ['bar']], // This is "right" based on how the function works
      search: ['hello+world'],
    });
  });

  test('search only', () => {
    window.location.search = '?search=hello+world';
    window.location.href = `https://example.com/${window.location.search}`;
    expect(parseQueryParams()).toMatchObject({
      search: ['hello+world'],
    });
  });

  test('multiple search args somehow', () => {
    window.location.search = '?search=hello+world&search=farewell+world';
    window.location.href = `https://example.com/${window.location.search}`;
    expect(parseQueryParams()).toMatchObject({
      search: ['hello+world', ['farewell+world']], // Again, this is expected, if a bit odd
    });
  });
});
