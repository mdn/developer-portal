window.addEventListener('DOMContentLoaded', () => {
  const menuButton = document.getElementById('nav-hamburger');
  if (menuButton) {
    menuButton.onclick = ((e) => {
      const menu = e.target.parentNode.querySelector('.nav-topics');
      menu.classList.toggle('nav-topics-open');
    });
  }
});
