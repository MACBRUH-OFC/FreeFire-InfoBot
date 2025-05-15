import { handleUpdate } from '../lib/bot';

export default async (req, res) => {
  if (req.method === 'POST') {
    try {
      const update = req.body;
      await handleUpdate(update);
      res.status(200).send('OK');
    } catch (error) {
      console.error('Error handling update:', error);
      res.status(500).send('Internal Server Error');
    }
  } else {
    res.status(405).send('Method Not Allowed');
  }
};
