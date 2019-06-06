/* eslint-disable class-methods-use-this */
class GetStarted {
  init() {
    if (document.getElementById('get-started')) {
      this.setInitialState();

      if (window.location.hash.length > 0) {
        this.showContent(window.location.hash);
      }

      window.addEventListener('hashchange', () => {
        this.showContent(window.location.hash);
      }, false);
    }
  }

  setInitialState() {
    let isFirst = true;
    Array.from(document.getElementsByClassName('get-started-content-panel')).forEach((el) => {
      if (!isFirst) {
        el.classList.remove('displayed');
      } else {
        isFirst = false;
      }
    });
    document.getElementById('get-started-nav').classList.remove('hidden');
  }

  showContent(hash) {
    if (hash.length > 0) {
      // show link as active
      Array.from(document.getElementsByClassName('get-started-toggle')).forEach((el) => {
        if (el.attributes.href.value === hash) {
          el.classList.add('active');
        } else {
          el.classList.remove('active');
        }
      });

      // show relevant content
      Array.from(document.getElementsByClassName('get-started-content-panel')).forEach((el) => {
        if (el.attributes['data-hash'].value === hash) {
          el.classList.add('displayed');
        } else {
          el.classList.remove('displayed');
        }
      });
    }
  }
}

export default GetStarted;
