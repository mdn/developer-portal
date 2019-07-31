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
  const formData = new FormData(form);
  return Array.from(formData.entries()).reduce((acc, [key, value]) => {
    if (!acc[key]) {
      acc[key] = [];
    }

    acc[key].push(value);
    return acc;
  }, {});
};
