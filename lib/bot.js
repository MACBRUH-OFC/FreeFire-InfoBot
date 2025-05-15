import TelegramBot from 'node-telegram-bot-api';
import { loadItemData, processImage, isAuthorized } from './utils';

const BOT_TOKEN = process.env.BOT_TOKEN || '';
const AUTHORIZED_GROUP_IDS = JSON.parse(process.env.AUTHORIZED_GROUP_IDS || '[]');
const AUTHORIZED_USER_IDS = JSON.parse(process.env.AUTHORIZED_USER_IDS || '[]');

let itemData = [];
let bot;

export async function initializeBot() {
  try {
    itemData = await loadItemData();
    bot = new TelegramBot(BOT_TOKEN, { polling: false });
    console.log('Bot initialized');
  } catch (error) {
    console.error('Error initializing bot:', error);
  }
}

export async function handleUpdate(update) {
  if (!bot) await initializeBot();
  
  if (update.message) {
    const chatId = update.message.chat.id;
    const messageText = update.message.text;
    const messageId = update.message.message_id;
    const userId = update.message.from.id;

    if (!isAuthorized(chatId, userId, AUTHORIZED_GROUP_IDS, AUTHORIZED_USER_IDS)) {
      return unauthorizedResponse(chatId, messageId);
    }

    if (messageText.startsWith('/start')) {
      return startCommand(chatId);
    }

    if (messageText.toLowerCase().startsWith('id ') && messageText.length > 3) {
      const itemIdStr = messageText.substring(3).trim();
      if (/^\d+$/.test(itemIdStr)) {
        const itemId = parseInt(itemIdStr);
        const foundItem = itemData.find(item => item.Id === itemId);
        
        if (foundItem) {
          return sendItemInfo(chatId, messageId, foundItem);
        } else {
          return bot.sendMessage(chatId, '❌ Wrong ID/Data Not Found', {
            reply_to_message_id: messageId
          });
        }
      }
    }
  }
}

async function startCommand(chatId) {
  const startMessage = `🎮 Free Fire Item Bot 🎮

Send item IDs in this format:
id (item id)

🔍 Get complete item details with images`;
  
  return bot.sendMessage(chatId, startMessage);
}

async function unauthorizedResponse(chatId, messageId) {
  return bot.sendMessage(
    chatId,
    `🚫 ACCESS RESTRICTED

This bot only works in official group
Join @FreeFire_MacbruhUpdates
to use all bot features`,
    { reply_to_message_id: messageId }
  );
}

async function sendItemInfo(chatId, messageId, item) {
  try {
    const IMAGE_BASE_URL = process.env.IMAGE_BASE_URL || 'https://raw.githubusercontent.com/MACBRUH-OFC/FreeFire-Resources/main/live/IconCDN/android/';
    const imageUrl = `${IMAGE_BASE_URL}${item.Id}.png`;
    const imageBuffer = await processImage(imageUrl);

    const caption = `▫️ ITEM DETAILS ▫️
➖➖➖➖➖➖➖
ID: ${item.Id}
Name: ${item.name}
Desc: ${item.desc}
Type: ${item.Type}
Icon: ${item.Icon}
➖➖➖➖➖➖➖`;

    if (imageBuffer) {
      return bot.sendPhoto(chatId, imageBuffer, {
        caption,
        reply_to_message_id: messageId
      });
    } else {
      return bot.sendMessage(chatId, `${caption}\n⚠️ Image not available`, {
        reply_to_message_id: messageId
      });
    }
  } catch (error) {
    console.error('Error sending item info:', error);
    return bot.sendMessage(chatId, '❌ Error processing item information', {
      reply_to_message_id: messageId
    });
  }
}
