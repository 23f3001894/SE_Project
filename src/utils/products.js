const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';
const API_ORIGIN = API_BASE_URL.replace(/\/api\/?$/, '');

export function resolveProductImage(imagePath) {
  if (!imagePath) {
    return `${API_ORIGIN}/static/images/product-placeholder.svg`;
  }

  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }

  return `${API_ORIGIN}${imagePath.startsWith('/') ? imagePath : `/${imagePath}`}`;
}
