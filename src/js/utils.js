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
    if (!acc[decodeURIComponent(key)]) {
      acc[decodeURIComponent(key)] = val;
    } else {
      acc[decodeURIComponent(key)].push(val);
    }
    return acc;
  }, {});
};

/**
 * Creates an object based on a form's current input values.
 *
 * @param {object} form
 * @returns {object}
 */
exports.parseForm = form => {
  const filter = {};
  const elements = form.querySelectorAll('input[type="checkbox"]:checked');
  Array.from(elements).forEach(element => {
    if (!filter[element.name]) {
      filter[element.name] = [];
    }
    filter[element.name].push(element.value);
  });
  return filter;
};
