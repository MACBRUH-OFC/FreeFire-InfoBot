import axios from 'axios';
import sharp from 'sharp';

const ITEM_DATA_URL = process.env.ITEM_DATA_URL || 'https://raw.githubusercontent.com/MACBRUH-OFC/FreeFire-Resources/refs/heads/main/data/itemData.json';

export async function loadItemData() {
  try {
    const response = await axios.get(ITEM_DATA_URL);
    return response.data;
  } catch (error) {
    console.error('Error loading item data:', error);
    return [];
  }
}

export async function processImage(imageUrl) {
  try {
    const response = await axios.get(imageUrl, {
      responseType: 'arraybuffer',
      timeout: 10000
    });

    let image = sharp(response.data);
    const metadata = await image.metadata();

    if (metadata.hasAlpha) {
      image = image.flatten({ background: '#000000' });
    }

    return image.png().toBuffer();
  } catch (error) {
    console.error('Image processing error:', error);
    return null;
  }
}

export function isAuthorized(chatId, userId, authorizedGroupIds, authorizedUserIds) {
  return authorizedGroupIds.includes(chatId) || 
         (chatId === userId && authorizedUserIds.includes(userId));
}
