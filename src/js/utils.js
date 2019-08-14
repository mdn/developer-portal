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
  if (!formData.entries) {
    // for IE
    let filter = {};
    const elements = document.getElementsByTagName("input");
    for (let i = 0; i < elements.length; i++) {
        const element = elements[i];
        if (element.type.toLowerCase() === "checkbox" && element.checked) {
          if (!filter[element.name]) {
            filter[element.name] = [];
          }
          filter[element.name].push(element.value);
        }
    }
    return filter;
  } else {
    return Array.from(formData.entries()).reduce((filter, [key, value]) => {
      if (!filter[key]) {
        filter[key] = [];
      }

      filter[key].push(value);
      return filter;
    }, {});
  }
};
