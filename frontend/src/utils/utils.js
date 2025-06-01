export const getDocumentPreviewImage = (post) => {
  // Return a data URL for a colored rectangle with the first letter of the title
  const firstLetter = post.title.charAt(0).toUpperCase();
  const canvas = document.createElement('canvas');
  canvas.width = 400;
  canvas.height = 300;
  const ctx = canvas.getContext('2d');
  
  // Fill background
  ctx.fillStyle = '#EAF2FD';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Draw letter
  ctx.fillStyle = '#333';
  ctx.font = 'bold 72px Arial';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(firstLetter, canvas.width / 2, canvas.height / 2);
  
  return canvas.toDataURL();
};

export const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};