/** Retrieves query parameters from the URL. Custom due to IE support. */
exports.parseQueryParams = () => {
  const { search } = window.location;

  if (!search) {
    return {};
  }

  const items = search.slice(1).split('&');
  return items.reduce((acc, item) => {
    const [key, value] = item.split('=');
    acc[decodeURIComponent(key)] = decodeURIComponent(value).split(',');
    return acc;
  }, {});
};

/** Creates an object based on a form's current input values. */
exports.parseForm = form => {
  if (FormData && FormData.prototype.entries) {
    const formData = new FormData(form);
    return Array.from(formData.entries()).reduce((filter, [key, value]) => {
      if (!filter[key]) {
        filter[key] = []; // eslint-disable-line no-param-reassign
      }
      filter[key].push(value);
      return filter;
    }, {});
  }

  const filter = {};
  const elements = document.querySelectorAll('input[type="checkbox"]:checked');
  Array.from(elements).forEach((element) => {
    if (!filter[element.name]) {
      filter[element.name] = [];
    }
    filter[element.name].push(element.value);
  });
  return filter;
};
