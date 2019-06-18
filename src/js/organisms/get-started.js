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
    document.querySelectorAll('.get-started-content-bg').forEach((el, idx) => {
      if (idx !== 0) {
        el.classList.remove('displayed');
      }
    });
    if (document.querySelectorAll('.get-started-toggle').length > 1) {
      document.getElementById('get-started-nav').classList.remove('hidden');
    }
  }

  showContent(hash) {
    if (hash.length > 0) {
      document.querySelectorAll('.get-started-toggle').forEach((el) => {
        if (el.attributes.href.value === hash) {
          el.className = 'get-started-toggle highlight2-inverse';
        } else {
          el.className = 'get-started-toggle highlight2';
        }
      });

      document.querySelectorAll('.get-started-content-bg').forEach((el) => {
        if (`#${el.attributes['data-hash'].value}` === hash) {
          el.classList.add('displayed');
        } else {
          el.classList.remove('displayed');
        }
      });
    }
  }
}

export default GetStarted;
