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

/**
 * Helper function to get cookie value given a cookie name
 *
 * @param {string} name  // cookie name
 * @returns {string}  // cookie value
 */
exports.getCookie = name => {
  let cookieValue = null;
  if (document.cookie) {
    const cookies = document.cookie.split(';');
    // eslint-disable-next-line no-restricted-syntax
    for (let cookie of cookies) {
      cookie = cookie.trim();

      // eslint-disable-next-line prefer-template
      const target = name + '=';
      // Does this cookie string begin with the name (and equals sign) we want?
      if (cookie.substring(0, name.length + 1) === target) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};
