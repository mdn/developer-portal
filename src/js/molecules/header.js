export default function headerInit() {
  const menuButton = document.getElementById('nav-hamburger');
  const menu = document.getElementById('nav-topics');
  if (menuButton) {
    menuButton.addEventListener('click', () => {
      menu.classList.toggle('nav-topics-open');
    });
  }
}
