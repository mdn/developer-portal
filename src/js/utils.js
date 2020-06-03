/**
 * Retrieves query parameters from the URL. Custom due to IE support.
 *
 * @returns {object}
 */
exports.parseQueryParams = () => {
  const { search } = window.location;

  if (!search) {
    return {};
  }

  const items = search.slice(1).split('&');
  return items.reduce((acc, item) => {
    const [key, value] = item.split('=');
    const val = decodeURIComponent(value).split(',');
    const decodedKey = decodeURIComponent(key);
    if (!acc[decodedKey]) {
      acc[decodedKey] = val;
    } else {
      acc[decodedKey].push(val);
    }
    return acc;
  }, {});
};

exports.decodeFormURLEncodedSpaces = (value) => {
  /* Turn "foo+bar" into "foo bar".
   * Context: decodeURIComponent (used above in parseQueryParams) does not
   * convert `+` to spaces, because the `+` is from the spec for
   * application/x-www-form-urlenconded, not encodeURIComponent)
   *
   * @param {string} value
   * @returns {string}
   */
  return value.replace(/\+/g, ' ');
};
