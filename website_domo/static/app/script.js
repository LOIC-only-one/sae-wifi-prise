const $card = document.querySelector('.box');
let bounds;

function rotateToMouse(e) {
  const mouseX = e.clientX;
  const mouseY = e.clientY;
  const leftX = mouseX - bounds.x;
  const topY = mouseY - bounds.y;
  const center = {
    x: leftX - bounds.width / 2,
    y: topY - bounds.height / 2
  }
  const distance = Math.sqrt(center.x**2 + center.y**2);
  
  $card.style.transform = `
    perspective(1000px)
    scale3d(1.03, 1.03, 1.03)
    rotate3d(
      ${center.y / 100},
      ${-center.x / 100},
      0,
      ${Math.log(distance) * 1.2}deg
    )
  `;
  
  // Apply the glow effect based on mouse position
  $card.querySelector('.glow').style.backgroundImage = `
    radial-gradient(
      circle at
      ${center.x * 1.2 + bounds.width / 2}px
      ${center.y * 1.2 + bounds.height / 2}px,
      #ffffff55,
      #0000000f
    )
  `;
}
$card.addEventListener('mouseenter', () => {
  bounds = $card.getBoundingClientRect();

  document.addEventListener('mousemove', rotateToMouse);
});

$card.addEventListener('mouseleave', () => {
  document.removeEventListener('mousemove', rotateToMouse);
  $card.style.transition = 'transform 0.1s, scale3d 0.1s';  // Make sure the reset is smooth
  $card.style.transform = 'perspective(1000px) scale3d(1, 1, 1) rotate3d(0, 0, 0, 0deg)';
});



